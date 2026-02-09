"""
Instagram Scraper Module

Platform-specific scraper for Instagram that implements:
- Instagram login authentication flow
- Post navigation and extraction
- Data parsing for Instagram post elements
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


class InstagramScraper(BaseScraper):
    """
    Instagram-specific scraper implementation.
    
    Handles Instagram's authentication flow, post extraction,
    and data parsing with support for pagination through scrolling.
    """
    
    # Instagram URLs
    LOGIN_URL = "https://www.instagram.com/accounts/login/"
    BASE_URL = "https://www.instagram.com"
    
    # Selectors (may need updates if Instagram changes their UI)
    SELECTORS = {
        'username_input': 'input[name="username"]',
        'password_input': 'input[name="password"]',
        'login_button': 'button[type="submit"]',
        'not_now_button': '//button[contains(text(), "Not Now")]',
        'save_info_not_now': '//button[contains(text(), "Not now")]',
        'article': 'article',
        'post_link': 'a[href*="/p/"]',
        'post_caption': 'h1',
        'post_likes': 'section > div > span',
        'post_timestamp': 'time',
        'post_author': 'header a',
        'hashtag': 'a[href*="/explore/tags/"]',
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
        Initialize Instagram scraper.
        
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
            logger_name='scraper.instagram'
        )
        
        self.logger.info("Instagram scraper initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate to Instagram using provided credentials.
        
        Implements Instagram login flow:
        1. Navigate to login page
        2. Enter username and password
        3. Click login button
        4. Handle "Save Login Info" and "Turn on Notifications" prompts
        5. Verify successful login
        
        Returns:
            bool: True if authentication successful
        
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            self.logger.info("Starting Instagram authentication...")
            
            # Navigate to login page
            self.logger.debug(f"Navigating to {self.LOGIN_URL}")
            self.driver.get(self.LOGIN_URL)
            
            # Wait for page to load and add human-like delay
            AntiDetection.human_like_delay(2, 4)
            
            # Wait for username input to be present
            wait = WebDriverWait(self.driver, 10)
            username_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['username_input']))
            )
            
            self.logger.debug("Login page loaded, entering credentials...")
            
            # Enter username with human-like typing
            username_input.clear()
            for char in self.credentials['username']:
                username_input.send_keys(char)
                time.sleep(0.1 + (time.time() % 0.1))  # Random delay between keystrokes
            
            AntiDetection.human_like_delay(0.5, 1.5)
            
            # Enter password
            password_input = self.driver.find_element(By.CSS_SELECTOR, self.SELECTORS['password_input'])
            password_input.clear()
            for char in self.credentials['password']:
                password_input.send_keys(char)
                time.sleep(0.1 + (time.time() % 0.1))
            
            AntiDetection.human_like_delay(0.5, 1.5)
            
            # Click login button
            self.logger.debug("Submitting login form...")
            login_button = self.driver.find_element(By.CSS_SELECTOR, self.SELECTORS['login_button'])
            login_button.click()
            
            # Wait for navigation after login
            AntiDetection.human_like_delay(3, 5)
            
            # Handle "Save Your Login Info?" prompt
            try:
                not_now_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.SELECTORS['not_now_button']))
                )
                self.logger.debug("Clicking 'Not Now' on save login info prompt")
                not_now_button.click()
                AntiDetection.human_like_delay(1, 2)
            except TimeoutException:
                self.logger.debug("No 'Save Login Info' prompt found")
            
            # Handle "Turn on Notifications" prompt
            try:
                not_now_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.SELECTORS['save_info_not_now']))
                )
                self.logger.debug("Clicking 'Not Now' on notifications prompt")
                not_now_button.click()
                AntiDetection.human_like_delay(1, 2)
            except TimeoutException:
                self.logger.debug("No 'Turn on Notifications' prompt found")
            
            # Verify successful login by checking if we're redirected away from login page
            current_url = self.driver.current_url
            if 'login' in current_url:
                # Still on login page - authentication likely failed
                self.logger.error(f"Authentication failed - still on login page: {current_url}")
                
                # Check for error messages
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, '#slfErrorAlert')
                    error_text = error_element.text
                    self.logger.error(f"Login error message: {error_text}")
                except NoSuchElementException:
                    self.logger.error("No specific error message found")
                
                raise AuthenticationError("Login failed - credentials may be incorrect")
            
            self.logger.info(f"Authentication successful - redirected to {current_url}")
            return True
            
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
        Scrape posts from Instagram target URL.
        
        Navigates to the target URL (user profile, hashtag, or explore page),
        scrolls to load posts, and extracts data from each post.
        
        Args:
            target_url: Instagram URL to scrape (profile, hashtag, etc.)
            limit: Maximum number of posts to scrape
        
        Returns:
            List of dictionaries containing post data
        
        Raises:
            ScraperError: If scraping fails
            TimeoutError: If execution exceeds timeout
        """
        posts = []
        seen_post_ids = set()
        scroll_attempts = 0
        max_scroll_attempts = 50  # Prevent infinite scrolling
        
        try:
            self.logger.info(f"Navigating to {target_url}")
            self.driver.get(target_url)
            
            # Wait for page to load
            AntiDetection.human_like_delay(2, 4)
            
            # Wait for articles (posts) to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['article'])))
            
            self.logger.info(f"Starting to scrape posts (limit: {limit})")
            
            while len(posts) < limit and scroll_attempts < max_scroll_attempts:
                # Check timeout
                self.check_timeout()
                
                # Apply rate limiting
                self.apply_rate_limiting()
                
                # Find all post links on current page
                post_links = self.driver.find_elements(By.CSS_SELECTOR, self.SELECTORS['post_link'])
                
                self.logger.debug(f"Found {len(post_links)} post links on page")
                
                # Extract data from new posts
                new_posts_found = False
                for link in post_links:
                    if len(posts) >= limit:
                        break
                    
                    try:
                        # Get post URL and extract post ID
                        post_url = link.get_attribute('href')
                        post_id = self._extract_post_id_from_url(post_url)
                        
                        # Skip if we've already seen this post
                        if post_id in seen_post_ids:
                            continue
                        
                        seen_post_ids.add(post_id)
                        new_posts_found = True
                        
                        # Extract post data
                        self.logger.debug(f"Extracting data for post {post_id}")
                        post_data = self._extract_post_data_from_feed(link, post_id, post_url)
                        
                        if post_data:
                            posts.append(post_data)
                            self.logger.info(f"Scraped post {len(posts)}/{limit}: {post_id}")
                        
                    except StaleElementReferenceException:
                        self.logger.warning("Stale element reference - element may have been removed")
                        continue
                    
                    except Exception as e:
                        self.logger.warning(f"Error extracting post data: {e}")
                        self.errors_encountered += 1
                        continue
                
                # If we've reached the limit, stop
                if len(posts) >= limit:
                    self.logger.info(f"Reached post limit: {len(posts)}/{limit}")
                    break
                
                # If no new posts found, try scrolling
                if not new_posts_found:
                    self.logger.debug("No new posts found, scrolling...")
                    self._scroll_page()
                    scroll_attempts += 1
                    AntiDetection.human_like_delay(2, 4)
                else:
                    scroll_attempts = 0  # Reset scroll attempts when we find new posts
            
            if scroll_attempts >= max_scroll_attempts:
                self.logger.warning(f"Reached maximum scroll attempts ({max_scroll_attempts})")
            
            self.logger.info(f"Scraping complete: {len(posts)} posts scraped")
            return posts
            
        except TimeoutException as e:
            self.logger.error(f"Timeout while scraping posts: {e}", exc_info=True)
            # Return partial results
            self.logger.info(f"Returning {len(posts)} posts scraped before timeout")
            return posts
        
        except Exception as e:
            self.logger.error(f"Error during post scraping: {e}", exc_info=True)
            # Return partial results
            self.logger.info(f"Returning {len(posts)} posts scraped before error")
            return posts
    
    def extract_post_data(self, post_element: Any) -> Dict[str, Any]:
        """
        Extract structured data from an Instagram post element.
        
        This method is required by BaseScraper but for Instagram,
        we use _extract_post_data_from_feed which is more suitable
        for Instagram's structure.
        
        Args:
            post_element: Selenium WebElement representing a post
        
        Returns:
            Dictionary with extracted post data
        """
        # This is a placeholder - Instagram scraping uses _extract_post_data_from_feed
        # which extracts data from the feed view rather than individual post elements
        raise NotImplementedError(
            "Use _extract_post_data_from_feed for Instagram post extraction"
        )
    
    def _extract_post_id_from_url(self, url: str) -> str:
        """
        Extract post ID from Instagram post URL.
        
        Args:
            url: Instagram post URL (e.g., https://www.instagram.com/p/ABC123/)
        
        Returns:
            Post ID string
        """
        # Instagram post URLs are in format: /p/{post_id}/
        match = re.search(r'/p/([^/]+)/', url)
        if match:
            return match.group(1)
        
        # Fallback: use the full URL as ID
        return url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
    
    def _extract_post_data_from_feed(
        self,
        link_element: Any,
        post_id: str,
        post_url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract post data from feed view.
        
        Extracts data from the post as it appears in the feed,
        without navigating to the individual post page.
        
        Args:
            link_element: Selenium WebElement for the post link
            post_id: Extracted post ID
            post_url: Full URL to the post
        
        Returns:
            Dictionary with post data, or None if extraction fails
        """
        try:
            # Navigate up to the article element containing this post
            article = link_element.find_element(By.XPATH, './ancestor::article')
            
            # Extract author
            author = "unknown"
            author_id = None
            try:
                author_link = article.find_element(By.CSS_SELECTOR, self.SELECTORS['post_author'])
                author = author_link.text or author_link.get_attribute('href').split('/')[-2]
                author_id = author_link.get_attribute('href').split('/')[-2]
            except NoSuchElementException:
                self.logger.debug(f"Could not find author for post {post_id}")
            
            # Extract caption/content
            content = ""
            try:
                # Try to find caption in various possible locations
                caption_elements = article.find_elements(By.TAG_NAME, 'h1')
                if not caption_elements:
                    caption_elements = article.find_elements(By.CSS_SELECTOR, 'span[dir="auto"]')
                
                if caption_elements:
                    # Get the first non-empty caption
                    for elem in caption_elements:
                        text = elem.text.strip()
                        if text and len(text) > len(content):
                            content = text
            except NoSuchElementException:
                self.logger.debug(f"Could not find caption for post {post_id}")
            
            # Extract likes count
            likes = 0
            try:
                likes_elements = article.find_elements(By.CSS_SELECTOR, 'section button span')
                for elem in likes_elements:
                    text = elem.text.strip()
                    # Look for numbers that might be likes
                    if text and text.replace(',', '').isdigit():
                        likes = int(text.replace(',', ''))
                        break
            except (NoSuchElementException, ValueError):
                self.logger.debug(f"Could not find likes count for post {post_id}")
            
            # Extract comments count
            comments_count = 0
            try:
                # Look for "View all X comments" text
                comments_elements = article.find_elements(By.CSS_SELECTOR, 'a[href*="/comments/"]')
                for elem in comments_elements:
                    text = elem.text.strip()
                    match = re.search(r'(\d+)', text)
                    if match:
                        comments_count = int(match.group(1))
                        break
            except (NoSuchElementException, ValueError):
                self.logger.debug(f"Could not find comments count for post {post_id}")
            
            # Extract timestamp
            timestamp = datetime.utcnow()
            try:
                time_element = article.find_element(By.CSS_SELECTOR, self.SELECTORS['post_timestamp'])
                datetime_attr = time_element.get_attribute('datetime')
                if datetime_attr:
                    # Parse ISO format timestamp
                    timestamp = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
            except (NoSuchElementException, ValueError):
                self.logger.debug(f"Could not find timestamp for post {post_id}, using current time")
            
            # Extract hashtags from content
            hashtags = []
            if content:
                hashtags = re.findall(r'#(\w+)', content)
            
            # Determine media type (basic detection)
            media_type = "unknown"
            try:
                # Check for video indicator
                if article.find_elements(By.CSS_SELECTOR, 'video'):
                    media_type = "video"
                elif article.find_elements(By.CSS_SELECTOR, 'img'):
                    media_type = "image"
                
                # Check for carousel indicator
                if article.find_elements(By.CSS_SELECTOR, 'button[aria-label*="Next"]'):
                    media_type = "carousel"
            except NoSuchElementException:
                pass
            
            # Build post data dictionary
            post_data = {
                'post_id': post_id,
                'platform': 'instagram',
                'author': author,
                'author_id': author_id,
                'content': content,
                'timestamp': timestamp.isoformat(),
                'likes': likes,
                'comments_count': comments_count,
                'shares': 0,  # Instagram doesn't show share count publicly
                'url': post_url,
                'media_type': media_type,
                'hashtags': hashtags
            }
            
            return post_data
            
        except Exception as e:
            self.logger.error(f"Error extracting post data for {post_id}: {e}", exc_info=True)
            return None
    
    def _scroll_page(self) -> None:
        """
        Scroll the page down to load more posts.
        
        Uses JavaScript to scroll to the bottom of the page,
        triggering Instagram's infinite scroll to load more content.
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
