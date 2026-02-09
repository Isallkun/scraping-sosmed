"""
Twitter Scraper Module

Platform-specific scraper for Twitter (X) that implements:
- Twitter login authentication flow
- Tweet navigation and extraction
- Data parsing for Twitter tweet elements
- Pagination and scrolling handling

Validates: Requirements 1.1, 1.2
"""

import time
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException
)

from scraper.scrapers.base_scraper import (
    BaseScraper,
    AuthenticationError,
    ScraperError,
    TimeoutError as ScraperTimeoutError
)
from scraper.utils.anti_detection import AntiDetection


class TwitterScraper(BaseScraper):
    """
    Twitter-specific scraper implementation.
    
    Handles Twitter's authentication flow, tweet extraction,
    and data parsing with support for pagination through scrolling.
    """
    
    # Twitter URLs
    LOGIN_URL = "https://twitter.com/i/flow/login"
    BASE_URL = "https://twitter.com"
    
    # Selectors (may need updates if Twitter changes their UI)
    SELECTORS = {
        'username_input': 'input[autocomplete="username"]',
        'password_input': 'input[name="password"]',
        'next_button': '//span[text()="Next"]',
        'login_button': '//span[text()="Log in"]',
        'tweet_article': 'article[data-testid="tweet"]',
        'tweet_text': '[data-testid="tweetText"]',
        'tweet_author': '[data-testid="User-Name"]',
        'tweet_time': 'time',
        'tweet_like': '[data-testid="like"]',
        'tweet_retweet': '[data-testid="retweet"]',
        'tweet_reply': '[data-testid="reply"]',
        'tweet_link': 'a[href*="/status/"]',
    }
    
    def __init__(
        self,
        credentials: Optional[Dict[str, str]] = None,
        rate_limit: int = 30,
        timeout: int = 300,
        headless: bool = True,
        max_retries: int = 5
    ):
        """
        Initialize Twitter scraper.
        
        Args:
            credentials: Dictionary with 'username' and 'password' keys
            rate_limit: Maximum requests per minute (default: 30)
            timeout: Maximum execution time in seconds (default: 300)
            headless: Whether to run browser in headless mode (default: True)
            max_retries: Maximum retry attempts for network errors (default: 5)
        """
        super().__init__(
            credentials=credentials,
            rate_limit=rate_limit,
            timeout=timeout,
            headless=headless,
            max_retries=max_retries,
            logger_name='scraper.twitter'
        )
        
        self.logger.info("Twitter scraper initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate to Twitter using provided credentials.
        
        Implements Twitter login flow:
        1. Navigate to login page
        2. Enter username and click Next
        3. Enter password and click Log in
        4. Handle any additional verification prompts
        5. Verify successful login
        
        Returns:
            bool: True if authentication successful
        
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            self.logger.info("Starting Twitter authentication...")
            
            # Navigate to login page
            self.logger.debug(f"Navigating to {self.LOGIN_URL}")
            self.driver.get(self.LOGIN_URL)
            
            # Wait for page to load and add human-like delay
            AntiDetection.human_like_delay(2, 4)
            
            # Wait for username input to be present
            wait = WebDriverWait(self.driver, 15)
            username_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['username_input']))
            )
            
            self.logger.debug("Login page loaded, entering username...")
            
            # Enter username with human-like typing
            username_input.clear()
            for char in self.credentials['username']:
                username_input.send_keys(char)
                time.sleep(0.1 + (time.time() % 0.1))  # Random delay between keystrokes
            
            AntiDetection.human_like_delay(0.5, 1.5)
            
            # Click Next button
            self.logger.debug("Clicking Next button...")
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, self.SELECTORS['next_button']))
            )
            next_button.click()
            
            AntiDetection.human_like_delay(2, 3)
            
            # Wait for password input
            self.logger.debug("Entering password...")
            password_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['password_input']))
            )
            
            # Enter password with human-like typing
            password_input.clear()
            for char in self.credentials['password']:
                password_input.send_keys(char)
                time.sleep(0.1 + (time.time() % 0.1))
            
            AntiDetection.human_like_delay(0.5, 1.5)
            
            # Click Log in button
            self.logger.debug("Submitting login form...")
            login_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, self.SELECTORS['login_button']))
            )
            login_button.click()
            
            # Wait for navigation after login
            AntiDetection.human_like_delay(3, 5)
            
            # Verify successful login by checking URL
            current_url = self.driver.current_url
            
            # If we're still on login page or see error, authentication failed
            if 'login' in current_url or 'flow' in current_url:
                self.logger.error(f"Authentication failed - still on login page: {current_url}")
                
                # Check for error messages
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, '[role="alert"]')
                    if error_elements:
                        error_text = error_elements[0].text
                        self.logger.error(f"Login error message: {error_text}")
                except Exception:
                    self.logger.error("No specific error message found")
                
                raise AuthenticationError("Login failed - credentials may be incorrect")
            
            # Check if we reached the home timeline (successful login)
            if 'home' in current_url or current_url == self.BASE_URL or current_url == f"{self.BASE_URL}/":
                self.logger.info(f"Authentication successful - redirected to {current_url}")
                return True
            
            # If we're on a different page, wait a bit more and check again
            AntiDetection.human_like_delay(2, 3)
            current_url = self.driver.current_url
            
            if 'login' not in current_url and 'flow' not in current_url:
                self.logger.info(f"Authentication successful - on page: {current_url}")
                return True
            
            # Still on login/flow page after waiting
            self.logger.error(f"Authentication uncertain - on page: {current_url}")
            raise AuthenticationError("Login verification failed - may need additional verification")
            
        except TimeoutException as e:
            self.logger.error(f"Timeout during authentication: {e}", exc_info=True)
            raise AuthenticationError(f"Authentication timeout: {e}")
        
        except NoSuchElementException as e:
            self.logger.error(f"Element not found during authentication: {e}", exc_info=True)
            raise AuthenticationError(f"Authentication failed - page structure may have changed: {e}")
        
        except Exception as e:
            self.logger.error(f"Unexpected error during authentication: {e}", exc_info=True)
            raise AuthenticationError(f"Authentication failed: {e}")
    
    def scrape_posts(self, target_url: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Scrape tweets from Twitter target URL.
        
        Navigates to the target URL (user profile, search, or timeline),
        scrolls to load tweets, and extracts data from each tweet.
        
        Args:
            target_url: Twitter URL to scrape (profile, search, etc.)
            limit: Maximum number of tweets to scrape
        
        Returns:
            List of dictionaries containing tweet data
        
        Raises:
            ScraperError: If scraping fails
            TimeoutError: If execution exceeds timeout
        """
        posts = []
        seen_post_ids = set()
        scroll_attempts = 0
        max_scroll_attempts = 50  # Prevent infinite scrolling
        no_new_posts_count = 0
        max_no_new_posts = 5  # Stop after 5 scrolls with no new posts
        
        try:
            self.logger.info(f"Navigating to {target_url}")
            self.driver.get(target_url)
            
            # Wait for page to load
            AntiDetection.human_like_delay(3, 5)
            
            # Wait for tweets to load
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['tweet_article'])))
            
            self.logger.info(f"Starting to scrape tweets (limit: {limit})")
            
            while len(posts) < limit and scroll_attempts < max_scroll_attempts:
                # Check timeout
                self.check_timeout()
                
                # Apply rate limiting
                self.apply_rate_limiting()
                
                # Find all tweet articles on current page
                tweet_articles = self.driver.find_elements(By.CSS_SELECTOR, self.SELECTORS['tweet_article'])
                
                self.logger.debug(f"Found {len(tweet_articles)} tweet articles on page")
                
                # Extract data from new tweets
                new_posts_found = False
                for article in tweet_articles:
                    if len(posts) >= limit:
                        break
                    
                    try:
                        # Extract tweet data
                        tweet_data = self._extract_tweet_data_from_article(article)
                        
                        if not tweet_data:
                            continue
                        
                        post_id = tweet_data['post_id']
                        
                        # Skip if we've already seen this tweet
                        if post_id in seen_post_ids:
                            continue
                        
                        seen_post_ids.add(post_id)
                        new_posts_found = True
                        
                        posts.append(tweet_data)
                        self.logger.info(f"Scraped tweet {len(posts)}/{limit}: {post_id}")
                        
                    except StaleElementReferenceException:
                        self.logger.warning("Stale element reference - element may have been removed")
                        continue
                    
                    except Exception as e:
                        self.logger.warning(f"Error extracting tweet data: {e}")
                        self.errors_encountered += 1
                        continue
                
                # If we've reached the limit, stop
                if len(posts) >= limit:
                    self.logger.info(f"Reached tweet limit: {len(posts)}/{limit}")
                    break
                
                # If no new posts found, try scrolling
                if not new_posts_found:
                    no_new_posts_count += 1
                    self.logger.debug(f"No new tweets found ({no_new_posts_count}/{max_no_new_posts}), scrolling...")
                    
                    if no_new_posts_count >= max_no_new_posts:
                        self.logger.info(f"No new tweets after {max_no_new_posts} scroll attempts, stopping")
                        break
                    
                    self._scroll_page()
                    scroll_attempts += 1
                    AntiDetection.human_like_delay(2, 4)
                else:
                    no_new_posts_count = 0  # Reset counter when we find new posts
                    scroll_attempts = 0  # Reset scroll attempts when we find new posts
            
            if scroll_attempts >= max_scroll_attempts:
                self.logger.warning(f"Reached maximum scroll attempts ({max_scroll_attempts})")
            
            self.logger.info(f"Scraping complete: {len(posts)} tweets scraped")
            return posts
            
        except TimeoutException as e:
            self.logger.error(f"Timeout while scraping tweets: {e}", exc_info=True)
            # Return partial results
            self.logger.info(f"Returning {len(posts)} tweets scraped before timeout")
            return posts
        
        except Exception as e:
            self.logger.error(f"Error during tweet scraping: {e}", exc_info=True)
            # Return partial results
            self.logger.info(f"Returning {len(posts)} tweets scraped before error")
            return posts
    
    def extract_post_data(self, post_element: Any) -> Dict[str, Any]:
        """
        Extract structured data from a Twitter tweet element.
        
        This method is required by BaseScraper but for Twitter,
        we use _extract_tweet_data_from_article which is more suitable
        for Twitter's structure.
        
        Args:
            post_element: Selenium WebElement representing a tweet
        
        Returns:
            Dictionary with extracted tweet data
        """
        # This is a placeholder - Twitter scraping uses _extract_tweet_data_from_article
        return self._extract_tweet_data_from_article(post_element)
    
    def _extract_post_id_from_url(self, url: str) -> str:
        """
        Extract tweet ID from Twitter status URL.
        
        Args:
            url: Twitter status URL (e.g., https://twitter.com/user/status/123456789)
        
        Returns:
            Tweet ID string
        """
        # Twitter status URLs are in format: /status/{tweet_id}
        match = re.search(r'/status/(\d+)', url)
        if match:
            return match.group(1)
        
        # Fallback: use timestamp-based ID
        return f"tweet_{int(time.time() * 1000)}"
    
    def _extract_tweet_data_from_article(self, article: Any) -> Optional[Dict[str, Any]]:
        """
        Extract tweet data from article element.
        
        Extracts data from the tweet as it appears in the timeline.
        
        Args:
            article: Selenium WebElement for the tweet article
        
        Returns:
            Dictionary with tweet data, or None if extraction fails
        """
        try:
            # Extract tweet URL and ID
            post_url = None
            post_id = None
            try:
                tweet_link = article.find_element(By.CSS_SELECTOR, self.SELECTORS['tweet_link'])
                post_url = tweet_link.get_attribute('href')
                post_id = self._extract_post_id_from_url(post_url)
            except NoSuchElementException:
                # Generate fallback ID if we can't find the link
                post_id = f"tweet_{int(time.time() * 1000000)}"
                self.logger.debug(f"Could not find tweet link, using generated ID: {post_id}")
            
            # Extract author information
            author = "unknown"
            author_id = None
            try:
                author_element = article.find_element(By.CSS_SELECTOR, self.SELECTORS['tweet_author'])
                author_text = author_element.text
                
                # Parse author text which typically contains display name and @username
                lines = author_text.split('\n')
                for line in lines:
                    if line.startswith('@'):
                        author = line[1:]  # Remove @ symbol
                        author_id = author
                        break
                
                # If we didn't find @username in text, try to extract from link
                if author == "unknown":
                    try:
                        author_link = author_element.find_element(By.TAG_NAME, 'a')
                        href = author_link.get_attribute('href')
                        # Extract username from URL like /username
                        username_match = re.search(r'twitter\.com/([^/]+)', href)
                        if username_match:
                            author = username_match.group(1)
                            author_id = author
                    except NoSuchElementException:
                        pass
                        
            except NoSuchElementException:
                self.logger.debug(f"Could not find author for tweet {post_id}")
            
            # Extract tweet text content
            content = ""
            try:
                tweet_text_element = article.find_element(By.CSS_SELECTOR, self.SELECTORS['tweet_text'])
                content = tweet_text_element.text.strip()
            except NoSuchElementException:
                self.logger.debug(f"Could not find tweet text for {post_id}")
            
            # Extract timestamp
            timestamp = datetime.utcnow()
            try:
                time_element = article.find_element(By.CSS_SELECTOR, self.SELECTORS['tweet_time'])
                datetime_attr = time_element.get_attribute('datetime')
                if datetime_attr:
                    # Parse ISO format timestamp
                    timestamp = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
            except (NoSuchElementException, ValueError) as e:
                self.logger.debug(f"Could not find timestamp for tweet {post_id}, using current time: {e}")
            
            # Extract engagement metrics (likes, retweets, replies)
            likes = 0
            retweets = 0
            replies = 0
            
            try:
                # Find like button and extract count
                like_button = article.find_element(By.CSS_SELECTOR, self.SELECTORS['tweet_like'])
                like_text = like_button.get_attribute('aria-label') or ""
                like_match = re.search(r'(\d+)', like_text)
                if like_match:
                    likes = int(like_match.group(1))
            except (NoSuchElementException, ValueError):
                self.logger.debug(f"Could not find likes count for tweet {post_id}")
            
            try:
                # Find retweet button and extract count
                retweet_button = article.find_element(By.CSS_SELECTOR, self.SELECTORS['tweet_retweet'])
                retweet_text = retweet_button.get_attribute('aria-label') or ""
                retweet_match = re.search(r'(\d+)', retweet_text)
                if retweet_match:
                    retweets = int(retweet_match.group(1))
            except (NoSuchElementException, ValueError):
                self.logger.debug(f"Could not find retweets count for tweet {post_id}")
            
            try:
                # Find reply button and extract count
                reply_button = article.find_element(By.CSS_SELECTOR, self.SELECTORS['tweet_reply'])
                reply_text = reply_button.get_attribute('aria-label') or ""
                reply_match = re.search(r'(\d+)', reply_text)
                if reply_match:
                    replies = int(reply_match.group(1))
            except (NoSuchElementException, ValueError):
                self.logger.debug(f"Could not find replies count for tweet {post_id}")
            
            # Extract hashtags from content
            hashtags = []
            if content:
                hashtags = re.findall(r'#(\w+)', content)
            
            # Determine media type
            media_type = "text"
            try:
                # Check for images
                if article.find_elements(By.CSS_SELECTOR, 'img[alt*="Image"]'):
                    media_type = "image"
                # Check for videos
                elif article.find_elements(By.CSS_SELECTOR, 'video'):
                    media_type = "video"
                # Check for GIFs
                elif article.find_elements(By.CSS_SELECTOR, '[data-testid="tweetPhoto"]'):
                    media_type = "image"
            except NoSuchElementException:
                pass
            
            # Build tweet data dictionary
            tweet_data = {
                'post_id': post_id,
                'platform': 'twitter',
                'author': author,
                'author_id': author_id,
                'content': content,
                'timestamp': timestamp.isoformat(),
                'likes': likes,
                'comments_count': replies,  # Twitter calls them replies
                'shares': retweets,  # Twitter's retweets are shares
                'url': post_url or f"https://twitter.com/{author}/status/{post_id}",
                'media_type': media_type,
                'hashtags': hashtags,
                'retweets': retweets,  # Additional Twitter-specific field
                'replies': replies  # Additional Twitter-specific field
            }
            
            return tweet_data
            
        except Exception as e:
            self.logger.error(f"Error extracting tweet data: {e}", exc_info=True)
            return None
    
    def _scroll_page(self) -> None:
        """
        Scroll the page down to load more tweets.
        
        Uses JavaScript to scroll to the bottom of the page,
        triggering Twitter's infinite scroll to load more content.
        """
        try:
            # Get current scroll position
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            AntiDetection.human_like_delay(2, 3)
            
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                self.logger.debug("No new content loaded after scroll")
            else:
                self.logger.debug(f"Page height increased from {last_height} to {new_height}")
                
        except Exception as e:
            self.logger.warning(f"Error during page scroll: {e}")
