"""
Facebook Scraper Module

Platform-specific scraper for Facebook that implements:
- Facebook login authentication flow
- Post navigation and extraction
- Data parsing for Facebook post elements
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


class FacebookScraper(BaseScraper):
    """
    Facebook-specific scraper implementation.
    
    Handles Facebook's authentication flow, post extraction,
    and data parsing with support for pagination through scrolling.
    """
    
    # Facebook URLs
    LOGIN_URL = "https://www.facebook.com/login"
    BASE_URL = "https://www.facebook.com"
    
    # Selectors (may need updates if Facebook changes their UI)
    SELECTORS = {
        'email_input': 'input[name="email"]',
        'password_input': 'input[name="pass"]',
        'login_button': 'button[name="login"]',
        'post_container': '[data-pagelet*="FeedUnit"]',
        'post_content': '[data-ad-preview="message"]',
        'post_author': 'a[role="link"] strong',
        'post_timestamp': 'a[aria-label*="ago"]',
        'post_like': '[aria-label*="Like"]',
        'post_comment': '[aria-label*="Comment"]',
        'post_share': '[aria-label*="Share"]',
        'post_link': 'a[href*="/posts/"]',
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
        Initialize Facebook scraper.
        
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
            logger_name='scraper.facebook'
        )
        
        self.logger.info("Facebook scraper initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate to Facebook using provided credentials.
        
        Implements Facebook login flow:
        1. Navigate to login page
        2. Enter email and password
        3. Click login button
        4. Handle any post-login prompts
        5. Verify successful login
        
        Returns:
            bool: True if authentication successful
        
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            self.logger.info("Starting Facebook authentication...")
            
            # Navigate to login page
            self.logger.debug(f"Navigating to {self.LOGIN_URL}")
            self.driver.get(self.LOGIN_URL)
            
            # Wait for page to load and add human-like delay
            AntiDetection.human_like_delay(2, 4)
            
            # Wait for email input to be present
            wait = WebDriverWait(self.driver, 15)
            email_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['email_input']))
            )
            
            self.logger.debug("Login page loaded, entering credentials...")
            
            # Enter email with human-like typing
            email_input.clear()
            for char in self.credentials['username']:
                email_input.send_keys(char)
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
            
            # Verify successful login by checking URL
            current_url = self.driver.current_url
            
            # If we're still on login page, authentication likely failed
            if 'login' in current_url:
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
            
            # Check if we reached the home feed (successful login)
            if current_url == self.BASE_URL or current_url == f"{self.BASE_URL}/" or 'home' in current_url:
                self.logger.info(f"Authentication successful - redirected to {current_url}")
                return True
            
            # If we're on a different page, wait a bit more and check again
            AntiDetection.human_like_delay(2, 3)
            current_url = self.driver.current_url
            
            if 'login' not in current_url:
                self.logger.info(f"Authentication successful - on page: {current_url}")
                return True
            
            # Still on login page after waiting
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
        Scrape posts from Facebook target URL.
        
        Navigates to the target URL (user profile, page, or group),
        scrolls to load posts, and extracts data from each post.
        
        Args:
            target_url: Facebook URL to scrape (profile, page, group, etc.)
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
        no_new_posts_count = 0
        max_no_new_posts = 5  # Stop after 5 scrolls with no new posts
        
        try:
            self.logger.info(f"Navigating to {target_url}")
            self.driver.get(target_url)
            
            # Wait for page to load
            AntiDetection.human_like_delay(3, 5)
            
            # Wait for posts to load
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['post_container'])))
            
            self.logger.info(f"Starting to scrape posts (limit: {limit})")
            
            while len(posts) < limit and scroll_attempts < max_scroll_attempts:
                # Check timeout
                self.check_timeout()
                
                # Apply rate limiting
                self.apply_rate_limiting()
                
                # Find all post containers on current page
                post_containers = self.driver.find_elements(By.CSS_SELECTOR, self.SELECTORS['post_container'])
                
                self.logger.debug(f"Found {len(post_containers)} post containers on page")
                
                # Extract data from new posts
                new_posts_found = False
                for container in post_containers:
                    if len(posts) >= limit:
                        break
                    
                    try:
                        # Extract post data
                        post_data = self._extract_post_data_from_container(container)
                        
                        if not post_data:
                            continue
                        
                        post_id = post_data['post_id']
                        
                        # Skip if we've already seen this post
                        if post_id in seen_post_ids:
                            continue
                        
                        seen_post_ids.add(post_id)
                        new_posts_found = True
                        
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
                    no_new_posts_count += 1
                    self.logger.debug(f"No new posts found ({no_new_posts_count}/{max_no_new_posts}), scrolling...")
                    
                    if no_new_posts_count >= max_no_new_posts:
                        self.logger.info(f"No new posts after {max_no_new_posts} scroll attempts, stopping")
                        break
                    
                    self._scroll_page()
                    scroll_attempts += 1
                    AntiDetection.human_like_delay(2, 4)
                else:
                    no_new_posts_count = 0  # Reset counter when we find new posts
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
        Extract structured data from a Facebook post element.
        
        This method is required by BaseScraper but for Facebook,
        we use _extract_post_data_from_container which is more suitable
        for Facebook's structure.
        
        Args:
            post_element: Selenium WebElement representing a post
        
        Returns:
            Dictionary with extracted post data
        """
        # This is a placeholder - Facebook scraping uses _extract_post_data_from_container
        return self._extract_post_data_from_container(post_element)
    
    def _extract_post_id_from_url(self, url: str) -> str:
        """
        Extract post ID from Facebook post URL.
        
        Args:
            url: Facebook post URL (e.g., https://facebook.com/user/posts/123456789)
        
        Returns:
            Post ID string
        """
        # Facebook post URLs can be in various formats
        # /posts/{post_id} or /permalink.php?story_fbid={post_id}
        match = re.search(r'/posts/(\d+)', url)
        if match:
            return match.group(1)
        
        match = re.search(r'story_fbid=(\d+)', url)
        if match:
            return match.group(1)
        
        match = re.search(r'/(\d+)/', url)
        if match:
            return match.group(1)
        
        # Fallback: use timestamp-based ID
        return f"fb_{int(time.time() * 1000)}"
    
    def _extract_post_data_from_container(self, container: Any) -> Optional[Dict[str, Any]]:
        """
        Extract post data from container element.
        
        Extracts data from the post as it appears in the feed.
        
        Args:
            container: Selenium WebElement for the post container
        
        Returns:
            Dictionary with post data, or None if extraction fails
        """
        try:
            # Extract post URL and ID
            post_url = None
            post_id = None
            try:
                post_link = container.find_element(By.CSS_SELECTOR, self.SELECTORS['post_link'])
                post_url = post_link.get_attribute('href')
                post_id = self._extract_post_id_from_url(post_url)
            except NoSuchElementException:
                # Generate fallback ID if we can't find the link
                post_id = f"fb_{int(time.time() * 1000000)}"
                self.logger.debug(f"Could not find post link, using generated ID: {post_id}")
            
            # Extract author information
            author = "unknown"
            author_id = None
            try:
                author_element = container.find_element(By.CSS_SELECTOR, self.SELECTORS['post_author'])
                author = author_element.text.strip()
                
                # Try to extract author ID from profile link
                try:
                    author_link = author_element.find_element(By.XPATH, './ancestor::a')
                    author_href = author_link.get_attribute('href')
                    # Extract ID from URL like /user.name or /profile.php?id=123
                    id_match = re.search(r'facebook\.com/([^/?]+)', author_href)
                    if id_match:
                        author_id = id_match.group(1)
                except NoSuchElementException:
                    pass
                        
            except NoSuchElementException:
                self.logger.debug(f"Could not find author for post {post_id}")
            
            # Extract post content
            content = ""
            try:
                content_element = container.find_element(By.CSS_SELECTOR, self.SELECTORS['post_content'])
                content = content_element.text.strip()
            except NoSuchElementException:
                self.logger.debug(f"Could not find content for post {post_id}")
            
            # Extract timestamp
            timestamp = datetime.utcnow()
            try:
                time_element = container.find_element(By.CSS_SELECTOR, self.SELECTORS['post_timestamp'])
                time_text = time_element.get_attribute('aria-label') or time_element.text
                
                # Try to parse relative time (e.g., "2 hours ago")
                # For now, use current time as fallback
                # TODO: Implement relative time parsing
                self.logger.debug(f"Found timestamp text: {time_text}")
                
            except NoSuchElementException:
                self.logger.debug(f"Could not find timestamp for post {post_id}, using current time")
            
            # Extract engagement metrics (likes, comments, shares)
            likes = 0
            comments_count = 0
            shares = 0
            
            try:
                # Find like button and extract count from aria-label
                like_button = container.find_element(By.CSS_SELECTOR, self.SELECTORS['post_like'])
                like_text = like_button.get_attribute('aria-label') or ""
                like_match = re.search(r'(\d+)', like_text)
                if like_match:
                    likes = int(like_match.group(1))
            except (NoSuchElementException, ValueError):
                self.logger.debug(f"Could not find likes count for post {post_id}")
            
            try:
                # Find comment button and extract count
                comment_button = container.find_element(By.CSS_SELECTOR, self.SELECTORS['post_comment'])
                comment_text = comment_button.get_attribute('aria-label') or ""
                comment_match = re.search(r'(\d+)', comment_text)
                if comment_match:
                    comments_count = int(comment_match.group(1))
            except (NoSuchElementException, ValueError):
                self.logger.debug(f"Could not find comments count for post {post_id}")
            
            try:
                # Find share button and extract count
                share_button = container.find_element(By.CSS_SELECTOR, self.SELECTORS['post_share'])
                share_text = share_button.get_attribute('aria-label') or ""
                share_match = re.search(r'(\d+)', share_text)
                if share_match:
                    shares = int(share_match.group(1))
            except (NoSuchElementException, ValueError):
                self.logger.debug(f"Could not find shares count for post {post_id}")
            
            # Extract hashtags from content
            hashtags = []
            if content:
                hashtags = re.findall(r'#(\w+)', content)
            
            # Determine media type
            media_type = "text"
            try:
                # Check for images
                if container.find_elements(By.CSS_SELECTOR, 'img[data-visualcompletion="media-vc-image"]'):
                    media_type = "image"
                # Check for videos
                elif container.find_elements(By.CSS_SELECTOR, 'video'):
                    media_type = "video"
            except NoSuchElementException:
                pass
            
            # Build post data dictionary
            post_data = {
                'post_id': post_id,
                'platform': 'facebook',
                'author': author,
                'author_id': author_id,
                'content': content,
                'timestamp': timestamp.isoformat(),
                'likes': likes,
                'comments_count': comments_count,
                'shares': shares,
                'url': post_url or f"https://facebook.com/{author}/posts/{post_id}",
                'media_type': media_type,
                'hashtags': hashtags
            }
            
            return post_data
            
        except Exception as e:
            self.logger.error(f"Error extracting post data: {e}", exc_info=True)
            return None
    
    def _scroll_page(self) -> None:
        """
        Scroll the page down to load more posts.
        
        Uses JavaScript to scroll to the bottom of the page,
        triggering Facebook's infinite scroll to load more content.
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
