"""
Base Scraper Module

Abstract base class for platform-specific scrapers with common functionality:
- WebDriver setup and management
- Rate limiting
- Timeout enforcement
- Retry logic with exponential backoff
- Error handling and logging

Validates: Requirements 1.1, 1.8, 11.1, 11.5
"""

import time
import traceback
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)

from scraper.utils.rate_limiter import RateLimiter
from scraper.utils.anti_detection import AntiDetection
from scraper.utils.logger import get_logger


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class AuthenticationError(ScraperError):
    """Raised when authentication fails."""
    pass


class NetworkError(ScraperError):
    """Raised when network operations fail."""
    pass


class TimeoutError(ScraperError):
    """Raised when operations exceed timeout."""
    pass


class BaseScraper(ABC):
    """
    Abstract base class for platform-specific scrapers.
    
    Provides common functionality:
    - WebDriver setup with anti-detection measures
    - Rate limiting to respect platform limits
    - Timeout enforcement to prevent infinite loops
    - Retry logic with exponential backoff for network errors
    - Error handling and logging
    
    Subclasses must implement:
    - authenticate(): Platform-specific authentication
    - scrape_posts(): Platform-specific post scraping
    - extract_post_data(): Platform-specific data extraction
    """
    
    def __init__(
        self,
        credentials: Optional[Dict[str, str]] = None,
        rate_limit: int = 30,
        timeout: int = 300,
        headless: bool = True,
        max_retries: int = 5,
        logger_name: Optional[str] = None
    ):
        """
        Initialize base scraper with configuration.
        
        Args:
            credentials: Dictionary with 'username' and 'password' keys (optional)
            rate_limit: Maximum requests per minute (default: 30)
            timeout: Maximum execution time in seconds (default: 300)
            headless: Whether to run browser in headless mode (default: True)
            max_retries: Maximum retry attempts for network errors (default: 5)
            logger_name: Name for logger (default: 'scraper.{platform}')
        
        Raises:
            ValueError: If configuration values are invalid
        """
        # Validate inputs
        if rate_limit <= 0:
            raise ValueError("rate_limit must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        
        # Store configuration
        self.credentials = credentials or {}
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.headless = headless
        self.max_retries = max_retries
        
        # Initialize components
        self.rate_limiter = RateLimiter(requests_per_minute=rate_limit)
        self.logger = get_logger(logger_name or f'scraper.{self.__class__.__name__.lower()}')
        
        # WebDriver instance (initialized in setup)
        self.driver: Optional[webdriver.Chrome] = None
        
        # Execution tracking
        self.start_time: Optional[float] = None
        self.posts_scraped: int = 0
        self.errors_encountered: int = 0
        
        self.logger.info(
            f"Initialized {self.__class__.__name__} with rate_limit={rate_limit}, "
            f"timeout={timeout}s, headless={headless}, max_retries={max_retries}"
        )
    
    def setup_driver(self) -> None:
        """
        Set up Selenium WebDriver with anti-detection measures.
        
        Configures Chrome WebDriver with:
        - Random user agent
        - Random viewport size
        - Headless mode (if configured)
        - Page load and script timeouts
        
        Raises:
            WebDriverException: If driver setup fails
        """
        try:
            self.logger.info("Setting up WebDriver...")
            
            # Get anti-detection parameters
            user_agent = AntiDetection.get_random_user_agent()
            viewport_width, viewport_height = AntiDetection.get_random_viewport()
            
            # Configure Chrome options
            chrome_options = ChromeOptions()
            
            # Set user agent
            chrome_options.add_argument(f'user-agent={user_agent}')
            
            # Set headless mode
            if self.headless:
                chrome_options.add_argument('--headless=new')
            
            # Additional anti-detection options
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Performance and stability options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'--window-size={viewport_width},{viewport_height}')
            
            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)  # 30 seconds for page load
            self.driver.set_script_timeout(30)     # 30 seconds for scripts
            
            # Set window size (for non-headless mode)
            if not self.headless:
                self.driver.set_window_size(viewport_width, viewport_height)
            
            # Execute script to hide webdriver property
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            self.logger.info(
                f"WebDriver setup complete: user_agent={user_agent[:50]}..., "
                f"viewport={viewport_width}x{viewport_height}, headless={self.headless}"
            )
            
        except WebDriverException as e:
            self.logger.error(f"Failed to setup WebDriver: {e}", exc_info=True)
            raise ScraperError(f"WebDriver setup failed: {e}")
    
    def check_timeout(self) -> None:
        """
        Check if execution has exceeded timeout limit.
        
        Raises:
            TimeoutError: If execution time exceeds configured timeout
        """
        if self.start_time is None:
            return
        
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout:
            error_msg = f"Execution timeout exceeded: {elapsed:.1f}s > {self.timeout}s"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg)
    
    def apply_rate_limiting(self) -> None:
        """
        Apply rate limiting before making requests.
        
        Blocks until a token is available from the rate limiter,
        ensuring requests don't exceed the configured rate limit.
        """
        self.rate_limiter.acquire()
        self.logger.debug("Rate limit token acquired")
    
    def retry_with_backoff(
        self,
        operation: callable,
        operation_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute operation with exponential backoff retry logic.
        
        Retries the operation up to max_retries times with exponential backoff:
        - Attempt 1: immediate
        - Attempt 2: wait 1 second
        - Attempt 3: wait 2 seconds
        - Attempt 4: wait 4 seconds
        - Attempt 5: wait 8 seconds
        
        Args:
            operation: Callable to execute
            operation_name: Name of operation for logging
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
        
        Returns:
            Result of successful operation
        
        Raises:
            NetworkError: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.debug(f"Attempting {operation_name} (attempt {attempt}/{self.max_retries})")
                result = operation(*args, **kwargs)
                
                if attempt > 1:
                    self.logger.info(f"{operation_name} succeeded on attempt {attempt}")
                
                return result
                
            except (WebDriverException, NetworkError, TimeoutException) as e:
                last_exception = e
                self.errors_encountered += 1
                
                if attempt < self.max_retries:
                    # Calculate backoff delay: 2^(attempt-1) seconds
                    backoff_delay = 2 ** (attempt - 1)
                    self.logger.warning(
                        f"{operation_name} failed on attempt {attempt}/{self.max_retries}: {e}. "
                        f"Retrying in {backoff_delay}s..."
                    )
                    time.sleep(backoff_delay)
                else:
                    self.logger.error(
                        f"{operation_name} failed after {self.max_retries} attempts: {e}",
                        exc_info=True
                    )
        
        # All retries exhausted
        raise NetworkError(
            f"{operation_name} failed after {self.max_retries} attempts: {last_exception}"
        )
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate to the platform.
        
        Platform-specific implementation must:
        - Navigate to login page
        - Enter credentials
        - Handle login flow
        - Verify successful authentication
        
        Returns:
            bool: True if authentication successful, False otherwise
        
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def scrape_posts(self, target_url: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Scrape posts from target URL.
        
        Platform-specific implementation must:
        - Navigate to target URL
        - Extract posts up to limit
        - Handle pagination/scrolling
        - Apply rate limiting between requests
        - Check timeout periodically
        
        Args:
            target_url: URL to scrape posts from
            limit: Maximum number of posts to scrape
        
        Returns:
            List of post dictionaries with extracted data
        
        Raises:
            ScraperError: If scraping fails
            TimeoutError: If execution exceeds timeout
        """
        pass
    
    @abstractmethod
    def extract_post_data(self, post_element: Any) -> Dict[str, Any]:
        """
        Extract structured data from a post element.
        
        Platform-specific implementation must extract:
        - post_id: Unique identifier
        - platform: Platform name (e.g., 'instagram')
        - author: Author username
        - content: Post text/caption
        - timestamp: Post creation time
        - likes: Number of likes
        - comments_count: Number of comments
        - shares: Number of shares (if applicable)
        
        Optional fields:
        - author_id: Author's unique ID
        - url: Direct URL to post
        - media_type: Type of media (image, video, etc.)
        - hashtags: List of hashtags
        
        Args:
            post_element: Selenium WebElement representing a post
        
        Returns:
            Dictionary with extracted post data
        
        Raises:
            NoSuchElementException: If required elements not found
        """
        pass
    
    def scrape(
        self,
        target_url: str,
        limit: int = 100,
        authenticate: bool = True
    ) -> Dict[str, Any]:
        """
        Main scraping workflow with error handling.
        
        Orchestrates the complete scraping process:
        1. Setup WebDriver
        2. Authenticate (if required)
        3. Scrape posts
        4. Handle errors gracefully
        5. Cleanup resources
        
        Args:
            target_url: URL to scrape
            limit: Maximum number of posts to scrape
            authenticate: Whether to authenticate before scraping
        
        Returns:
            Dictionary with metadata and scraped posts:
            {
                'metadata': {
                    'platform': str,
                    'scraped_at': str (ISO format),
                    'target_url': str,
                    'total_posts': int,
                    'execution_time_ms': int,
                    'errors_encountered': int
                },
                'posts': List[Dict]
            }
        
        Raises:
            ScraperError: If scraping fails critically
        """
        self.start_time = time.time()
        posts = []
        
        try:
            # Setup WebDriver
            self.setup_driver()
            
            # Authenticate if required
            if authenticate:
                if not self.credentials.get('username') or not self.credentials.get('password'):
                    self.logger.warning("No credentials provided, skipping authentication")
                else:
                    self.logger.info("Authenticating...")
                    auth_success = self.retry_with_backoff(
                        self.authenticate,
                        "authentication"
                    )
                    
                    if not auth_success:
                        raise AuthenticationError("Authentication failed")
                    
                    self.logger.info("Authentication successful")
            
            # Scrape posts
            self.logger.info(f"Starting to scrape posts from {target_url} (limit: {limit})")
            posts = self.scrape_posts(target_url, limit)
            self.posts_scraped = len(posts)
            
            self.logger.info(
                f"Scraping complete: {self.posts_scraped} posts scraped, "
                f"{self.errors_encountered} errors encountered"
            )
            
        except AuthenticationError as e:
            self.logger.error(f"Authentication failed: {e}", exc_info=True)
            raise
            
        except TimeoutError as e:
            self.logger.error(f"Timeout exceeded: {e}", exc_info=True)
            # Save partial data before raising
            if posts:
                self.logger.info(f"Saving {len(posts)} posts scraped before timeout")
            raise
            
        except Exception as e:
            self.logger.error(
                f"Unexpected error during scraping: {e}",
                exc_info=True
            )
            # Save partial data before raising
            if posts:
                self.logger.info(f"Saving {len(posts)} posts scraped before error")
            raise ScraperError(f"Scraping failed: {e}")
            
        finally:
            # Always cleanup
            self.close()
        
        # Calculate execution time
        execution_time_ms = int((time.time() - self.start_time) * 1000)
        
        # Build result with metadata
        result = {
            'metadata': {
                'platform': self.__class__.__name__.replace('Scraper', '').lower(),
                'scraped_at': datetime.utcnow().isoformat() + 'Z',
                'target_url': target_url,
                'total_posts': len(posts),
                'execution_time_ms': execution_time_ms,
                'errors_encountered': self.errors_encountered
            },
            'posts': posts
        }
        
        return result
    
    def close(self) -> None:
        """
        Clean up resources and close WebDriver.
        
        Safely closes the WebDriver and releases resources.
        Logs any errors during cleanup but doesn't raise exceptions.
        """
        if self.driver:
            try:
                self.logger.info("Closing WebDriver...")
                self.driver.quit()
                self.driver = None
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()
        return False  # Don't suppress exceptions
    
    def __repr__(self) -> str:
        """String representation of scraper."""
        return (
            f"{self.__class__.__name__}("
            f"rate_limit={self.rate_limit}, "
            f"timeout={self.timeout}, "
            f"headless={self.headless}, "
            f"max_retries={self.max_retries})"
        )
