"""
Unit tests for BaseScraper class.

Tests cover:
- Initialization and configuration validation
- WebDriver setup
- Rate limiting integration
- Timeout enforcement
- Retry logic with exponential backoff
- Error handling
- Resource cleanup
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch, call
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException
)

from scraper.scrapers.base_scraper import (
    BaseScraper,
    ScraperError,
    AuthenticationError,
    NetworkError,
    TimeoutError as ScraperTimeoutError
)


# Concrete implementation for testing
class TestScraper(BaseScraper):
    """Concrete scraper implementation for testing."""
    
    def authenticate(self) -> bool:
        """Mock authentication."""
        return True
    
    def scrape_posts(self, target_url: str, limit: int = 100):
        """Mock scrape_posts."""
        return []
    
    def extract_post_data(self, post_element):
        """Mock extract_post_data."""
        return {}


class TestBaseScraperInitialization:
    """Test BaseScraper initialization and configuration."""
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        scraper = TestScraper()
        
        assert scraper.credentials == {}
        assert scraper.rate_limit == 30
        assert scraper.timeout == 300
        assert scraper.headless is True
        assert scraper.max_retries == 5
        assert scraper.driver is None
        assert scraper.posts_scraped == 0
        assert scraper.errors_encountered == 0
    
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        credentials = {'username': 'test', 'password': 'pass'}
        scraper = TestScraper(
            credentials=credentials,
            rate_limit=60,
            timeout=600,
            headless=False,
            max_retries=3
        )
        
        assert scraper.credentials == credentials
        assert scraper.rate_limit == 60
        assert scraper.timeout == 600
        assert scraper.headless is False
        assert scraper.max_retries == 3
    
    def test_init_invalid_rate_limit(self):
        """Test initialization with invalid rate limit."""
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            TestScraper(rate_limit=0)
        
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            TestScraper(rate_limit=-1)
    
    def test_init_invalid_timeout(self):
        """Test initialization with invalid timeout."""
        with pytest.raises(ValueError, match="timeout must be positive"):
            TestScraper(timeout=0)
        
        with pytest.raises(ValueError, match="timeout must be positive"):
            TestScraper(timeout=-1)
    
    def test_init_invalid_max_retries(self):
        """Test initialization with invalid max_retries."""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            TestScraper(max_retries=-1)
    
    def test_rate_limiter_initialized(self):
        """Test that rate limiter is properly initialized."""
        scraper = TestScraper(rate_limit=60)
        
        assert scraper.rate_limiter is not None
        assert scraper.rate_limiter.requests_per_minute == 60
    
    def test_logger_initialized(self):
        """Test that logger is properly initialized."""
        scraper = TestScraper()
        
        assert scraper.logger is not None
        assert 'scraper' in scraper.logger.name.lower()


class TestBaseScraperWebDriverSetup:
    """Test WebDriver setup functionality."""
    
    @patch('scraper.scrapers.base_scraper.webdriver.Chrome')
    @patch('scraper.scrapers.base_scraper.AntiDetection')
    def test_setup_driver_success(self, mock_anti_detection, mock_chrome):
        """Test successful WebDriver setup."""
        # Mock anti-detection
        mock_anti_detection.get_random_user_agent.return_value = 'Mozilla/5.0 Test'
        mock_anti_detection.get_random_viewport.return_value = (1920, 1080)
        
        # Mock Chrome driver
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        scraper = TestScraper()
        scraper.setup_driver()
        
        # Verify driver was created
        assert mock_chrome.called
        assert scraper.driver == mock_driver
        
        # Verify timeouts were set
        mock_driver.set_page_load_timeout.assert_called_once_with(30)
        mock_driver.set_script_timeout.assert_called_once_with(30)
        
        # Verify anti-automation script was executed
        assert mock_driver.execute_script.called
    
    @patch('scraper.scrapers.base_scraper.webdriver.Chrome')
    @patch('scraper.scrapers.base_scraper.AntiDetection')
    def test_setup_driver_headless_mode(self, mock_anti_detection, mock_chrome):
        """Test WebDriver setup in headless mode."""
        mock_anti_detection.get_random_user_agent.return_value = 'Mozilla/5.0 Test'
        mock_anti_detection.get_random_viewport.return_value = (1920, 1080)
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        scraper = TestScraper(headless=True)
        scraper.setup_driver()
        
        # Check that Chrome was called with options
        assert mock_chrome.called
        options = mock_chrome.call_args[1]['options']
        
        # Verify headless argument is in options
        assert any('--headless' in arg for arg in options.arguments)
    
    @patch('scraper.scrapers.base_scraper.webdriver.Chrome')
    @patch('scraper.scrapers.base_scraper.AntiDetection')
    def test_setup_driver_non_headless_mode(self, mock_anti_detection, mock_chrome):
        """Test WebDriver setup in non-headless mode."""
        mock_anti_detection.get_random_user_agent.return_value = 'Mozilla/5.0 Test'
        mock_anti_detection.get_random_viewport.return_value = (1920, 1080)
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        scraper = TestScraper(headless=False)
        scraper.setup_driver()
        
        # Verify set_window_size was called for non-headless
        mock_driver.set_window_size.assert_called_once_with(1920, 1080)
    
    @patch('scraper.scrapers.base_scraper.webdriver.Chrome')
    def test_setup_driver_failure(self, mock_chrome):
        """Test WebDriver setup failure handling."""
        # Mock Chrome to raise exception
        mock_chrome.side_effect = WebDriverException("Driver not found")
        
        scraper = TestScraper()
        
        with pytest.raises(ScraperError, match="WebDriver setup failed"):
            scraper.setup_driver()


class TestBaseScraperTimeoutEnforcement:
    """Test timeout enforcement functionality."""
    
    def test_check_timeout_not_started(self):
        """Test check_timeout when scraping hasn't started."""
        scraper = TestScraper(timeout=1)
        
        # Should not raise when start_time is None
        scraper.check_timeout()
    
    def test_check_timeout_within_limit(self):
        """Test check_timeout when within time limit."""
        scraper = TestScraper(timeout=10)
        scraper.start_time = time.time()
        
        # Should not raise when within timeout
        scraper.check_timeout()
    
    def test_check_timeout_exceeded(self):
        """Test check_timeout when timeout is exceeded."""
        scraper = TestScraper(timeout=1)
        scraper.start_time = time.time() - 2  # 2 seconds ago
        
        with pytest.raises(ScraperTimeoutError, match="Execution timeout exceeded"):
            scraper.check_timeout()


class TestBaseScraperRateLimiting:
    """Test rate limiting functionality."""
    
    def test_apply_rate_limiting(self):
        """Test that rate limiting is applied."""
        scraper = TestScraper(rate_limit=60)
        
        # Mock the rate limiter
        scraper.rate_limiter = Mock()
        scraper.rate_limiter.acquire = Mock()
        
        scraper.apply_rate_limiting()
        
        # Verify acquire was called
        scraper.rate_limiter.acquire.assert_called_once()
    
    def test_rate_limiting_blocks_requests(self):
        """Test that rate limiting actually blocks rapid requests."""
        scraper = TestScraper(rate_limit=60)  # 60 requests per minute = 1 per second
        
        # Exhaust the initial token bucket
        for _ in range(60):
            scraper.rate_limiter.acquire(blocking=False)
        
        # Now measure time for requests that must wait
        start = time.time()
        scraper.apply_rate_limiting()
        elapsed = time.time() - start
        
        # Should have to wait for token refill (at least 0.9 seconds)
        assert elapsed > 0.9


class TestBaseScraperRetryLogic:
    """Test retry logic with exponential backoff."""
    
    def test_retry_success_first_attempt(self):
        """Test successful operation on first attempt."""
        scraper = TestScraper(max_retries=3)
        
        mock_operation = Mock(return_value="success")
        
        result = scraper.retry_with_backoff(mock_operation, "test_op")
        
        assert result == "success"
        assert mock_operation.call_count == 1
        assert scraper.errors_encountered == 0
    
    def test_retry_success_after_failures(self):
        """Test successful operation after some failures."""
        scraper = TestScraper(max_retries=3)
        
        # Fail twice, then succeed
        mock_operation = Mock(
            side_effect=[
                WebDriverException("Error 1"),
                WebDriverException("Error 2"),
                "success"
            ]
        )
        
        result = scraper.retry_with_backoff(mock_operation, "test_op")
        
        assert result == "success"
        assert mock_operation.call_count == 3
        assert scraper.errors_encountered == 2
    
    def test_retry_all_attempts_fail(self):
        """Test when all retry attempts fail."""
        scraper = TestScraper(max_retries=3)
        
        mock_operation = Mock(side_effect=WebDriverException("Persistent error"))
        
        with pytest.raises(NetworkError, match="failed after 3 attempts"):
            scraper.retry_with_backoff(mock_operation, "test_op")
        
        assert mock_operation.call_count == 3
        assert scraper.errors_encountered == 3
    
    @patch('time.sleep')
    def test_retry_exponential_backoff(self, mock_sleep):
        """Test that exponential backoff delays are correct."""
        scraper = TestScraper(max_retries=4)
        
        mock_operation = Mock(side_effect=WebDriverException("Error"))
        
        with pytest.raises(NetworkError):
            scraper.retry_with_backoff(mock_operation, "test_op")
        
        # Verify exponential backoff: 1s, 2s, 4s
        expected_delays = [1, 2, 4]
        actual_delays = [call_args[0][0] for call_args in mock_sleep.call_args_list]
        
        assert actual_delays == expected_delays
    
    def test_retry_with_arguments(self):
        """Test retry with operation arguments."""
        scraper = TestScraper(max_retries=2)
        
        mock_operation = Mock(return_value="result")
        
        result = scraper.retry_with_backoff(
            mock_operation,
            "test_op",
            "arg1",
            "arg2",
            kwarg1="value1"
        )
        
        assert result == "result"
        mock_operation.assert_called_once_with("arg1", "arg2", kwarg1="value1")


class TestBaseScraperErrorHandling:
    """Test error handling in scrape workflow."""
    
    @patch.object(TestScraper, 'setup_driver')
    @patch.object(TestScraper, 'authenticate')
    @patch.object(TestScraper, 'scrape_posts')
    def test_scrape_authentication_error(self, mock_scrape, mock_auth, mock_setup):
        """Test handling of authentication errors."""
        mock_auth.return_value = False
        
        scraper = TestScraper(credentials={'username': 'test', 'password': 'pass'})
        
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            scraper.scrape("http://example.com", limit=10)
        
        # Verify cleanup was called
        assert scraper.driver is None
    
    @patch.object(TestScraper, 'setup_driver')
    @patch.object(TestScraper, 'scrape_posts')
    def test_scrape_timeout_error(self, mock_scrape, mock_setup):
        """Test handling of timeout errors."""
        # Mock scrape_posts to raise timeout
        mock_scrape.side_effect = ScraperTimeoutError("Timeout")
        
        scraper = TestScraper()
        
        with pytest.raises(ScraperTimeoutError):
            scraper.scrape("http://example.com", limit=10, authenticate=False)
    
    @patch.object(TestScraper, 'setup_driver')
    @patch.object(TestScraper, 'scrape_posts')
    def test_scrape_unexpected_error(self, mock_scrape, mock_setup):
        """Test handling of unexpected errors."""
        mock_scrape.side_effect = Exception("Unexpected error")
        
        scraper = TestScraper()
        
        with pytest.raises(ScraperError, match="Scraping failed"):
            scraper.scrape("http://example.com", limit=10, authenticate=False)
    
    @patch.object(TestScraper, 'setup_driver')
    @patch.object(TestScraper, 'authenticate')
    @patch.object(TestScraper, 'scrape_posts')
    def test_scrape_success(self, mock_scrape, mock_auth, mock_setup):
        """Test successful scraping workflow."""
        mock_auth.return_value = True
        mock_scrape.return_value = [
            {'post_id': '1', 'content': 'Test post 1'},
            {'post_id': '2', 'content': 'Test post 2'}
        ]
        
        scraper = TestScraper(credentials={'username': 'test', 'password': 'pass'})
        result = scraper.scrape("http://example.com", limit=10)
        
        # Verify result structure
        assert 'metadata' in result
        assert 'posts' in result
        assert result['metadata']['total_posts'] == 2
        assert len(result['posts']) == 2
        assert result['metadata']['target_url'] == "http://example.com"
    
    @patch.object(TestScraper, 'setup_driver')
    @patch.object(TestScraper, 'scrape_posts')
    def test_scrape_without_authentication(self, mock_scrape, mock_setup):
        """Test scraping without authentication."""
        mock_scrape.return_value = []
        
        scraper = TestScraper()
        result = scraper.scrape("http://example.com", limit=10, authenticate=False)
        
        assert 'metadata' in result
        assert 'posts' in result


class TestBaseScraperResourceCleanup:
    """Test resource cleanup functionality."""
    
    def test_close_with_driver(self):
        """Test closing scraper with active driver."""
        scraper = TestScraper()
        mock_driver = Mock()
        scraper.driver = mock_driver
        
        scraper.close()
        
        # Verify driver.quit() was called
        mock_driver.quit.assert_called_once()
        assert scraper.driver is None
    
    def test_close_without_driver(self):
        """Test closing scraper without driver."""
        scraper = TestScraper()
        
        # Should not raise exception
        scraper.close()
    
    def test_close_with_error(self):
        """Test closing scraper when quit() raises error."""
        scraper = TestScraper()
        scraper.driver = Mock()
        scraper.driver.quit.side_effect = Exception("Quit error")
        
        # Should not raise exception, just log warning
        scraper.close()
    
    def test_context_manager(self):
        """Test scraper as context manager."""
        with TestScraper() as scraper:
            assert scraper is not None
        
        # Verify cleanup was called (driver should be None)
        assert scraper.driver is None
    
    @patch.object(TestScraper, 'setup_driver')
    def test_context_manager_with_exception(self, mock_setup):
        """Test context manager cleanup on exception."""
        scraper = None
        
        try:
            with TestScraper() as s:
                scraper = s
                scraper.driver = Mock()
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify cleanup was called even with exception
        assert scraper.driver is None


class TestBaseScraperAbstractMethods:
    """Test that abstract methods must be implemented."""
    
    def test_cannot_instantiate_base_scraper(self):
        """Test that BaseScraper cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseScraper()
    
    def test_concrete_scraper_must_implement_authenticate(self):
        """Test that concrete scraper must implement authenticate."""
        class IncompleteScraper(BaseScraper):
            def scrape_posts(self, target_url, limit=100):
                return []
            
            def extract_post_data(self, post_element):
                return {}
        
        with pytest.raises(TypeError):
            IncompleteScraper()
    
    def test_concrete_scraper_must_implement_scrape_posts(self):
        """Test that concrete scraper must implement scrape_posts."""
        class IncompleteScraper(BaseScraper):
            def authenticate(self):
                return True
            
            def extract_post_data(self, post_element):
                return {}
        
        with pytest.raises(TypeError):
            IncompleteScraper()
    
    def test_concrete_scraper_must_implement_extract_post_data(self):
        """Test that concrete scraper must implement extract_post_data."""
        class IncompleteScraper(BaseScraper):
            def authenticate(self):
                return True
            
            def scrape_posts(self, target_url, limit=100):
                return []
        
        with pytest.raises(TypeError):
            IncompleteScraper()


class TestBaseScraperRepr:
    """Test string representation."""
    
    def test_repr(self):
        """Test __repr__ method."""
        scraper = TestScraper(
            rate_limit=60,
            timeout=600,
            headless=False,
            max_retries=3
        )
        
        repr_str = repr(scraper)
        
        assert 'TestScraper' in repr_str
        assert 'rate_limit=60' in repr_str
        assert 'timeout=600' in repr_str
        assert 'headless=False' in repr_str
        assert 'max_retries=3' in repr_str
