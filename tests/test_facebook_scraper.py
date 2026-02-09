"""
Unit Tests for Facebook Scraper

Tests the FacebookScraper class functionality including:
- Initialization and configuration
- Post ID extraction
- Data extraction methods
- Error handling

Validates: Requirements 1.1, 1.2
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from scraper.scrapers.facebook import FacebookScraper
from scraper.scrapers.base_scraper import AuthenticationError


class TestFacebookScraperInitialization:
    """Test FacebookScraper initialization and configuration."""
    
    def test_initialization_with_defaults(self):
        """Test scraper initializes with default parameters."""
        scraper = FacebookScraper()
        
        assert scraper.rate_limit == 30
        assert scraper.timeout == 300
        assert scraper.headless is True
        assert scraper.max_retries == 5
        assert scraper.credentials == {}
    
    def test_initialization_with_credentials(self):
        """Test scraper initializes with provided credentials."""
        credentials = {'username': 'test_user', 'password': 'test_pass'}
        scraper = FacebookScraper(credentials=credentials)
        
        assert scraper.credentials == credentials
    
    def test_initialization_with_custom_parameters(self):
        """Test scraper initializes with custom parameters."""
        scraper = FacebookScraper(
            credentials={'username': 'test', 'password': 'pass'},
            rate_limit=20,
            timeout=600,
            headless=False,
            max_retries=3
        )
        
        assert scraper.rate_limit == 20
        assert scraper.timeout == 600
        assert scraper.headless is False
        assert scraper.max_retries == 3


class TestFacebookScraperHelperMethods:
    """Test FacebookScraper helper methods."""
    
    def test_extract_post_id_from_standard_url(self):
        """Test extracting post ID from standard Facebook URL."""
        scraper = FacebookScraper()
        
        url = "https://facebook.com/user/posts/1234567890"
        post_id = scraper._extract_post_id_from_url(url)
        
        assert post_id == "1234567890"
    
    def test_extract_post_id_from_permalink_url(self):
        """Test extracting post ID from permalink URL."""
        scraper = FacebookScraper()
        
        url = "https://facebook.com/permalink.php?story_fbid=9876543210"
        post_id = scraper._extract_post_id_from_url(url)
        
        assert post_id == "9876543210"
    
    def test_extract_post_id_from_malformed_url(self):
        """Test extracting post ID from malformed URL falls back gracefully."""
        scraper = FacebookScraper()
        
        url = "https://facebook.com/some/weird/path/"
        post_id = scraper._extract_post_id_from_url(url)
        
        # Should return a fallback ID starting with "fb_"
        assert post_id.startswith("fb_")


class TestFacebookScraperDataExtraction:
    """Test FacebookScraper data extraction methods."""
    
    def test_extract_post_data_from_container_with_complete_data(self):
        """Test extracting complete post data from container element."""
        scraper = FacebookScraper()
        
        # Mock the container element
        mock_container = Mock()
        
        # Mock post link
        mock_link = Mock()
        mock_link.get_attribute.return_value = "https://facebook.com/testuser/posts/123456789"
        
        # Mock author element
        mock_author = Mock()
        mock_author.text = "Test User"
        mock_author_link = Mock()
        mock_author_link.get_attribute.return_value = "https://facebook.com/testuser"
        mock_author.find_element.return_value = mock_author_link
        
        # Mock content element
        mock_content = Mock()
        mock_content.text = "This is a test post #testing"
        
        # Mock timestamp element
        mock_time = Mock()
        mock_time.get_attribute.return_value = "2 hours ago"
        mock_time.text = "2 hours ago"
        
        # Mock engagement buttons
        mock_like = Mock()
        mock_like.get_attribute.return_value = "10 Likes"
        
        mock_comment = Mock()
        mock_comment.get_attribute.return_value = "5 Comments"
        
        mock_share = Mock()
        mock_share.get_attribute.return_value = "3 Shares"
        
        # Setup find_element to return appropriate mocks
        def find_element_side_effect(by, selector):
            selector_map = {
                'a[href*="/posts/"]': mock_link,
                'a[role="link"] strong': mock_author,
                '[data-ad-preview="message"]': mock_content,
                'a[aria-label*="ago"]': mock_time,
                '[aria-label*="Like"]': mock_like,
                '[aria-label*="Comment"]': mock_comment,
                '[aria-label*="Share"]': mock_share,
            }
            return selector_map.get(selector, Mock())
        
        mock_container.find_element = Mock(side_effect=find_element_side_effect)
        mock_container.find_elements.return_value = []  # No media elements
        
        # Extract data
        post_data = scraper._extract_post_data_from_container(mock_container)
        
        # Verify extracted data
        assert post_data is not None
        assert post_data['post_id'] == "123456789"
        assert post_data['platform'] == 'facebook'
        assert post_data['author'] == 'Test User'
        assert post_data['content'] == "This is a test post #testing"
        assert post_data['likes'] == 10
        assert post_data['comments_count'] == 5
        assert post_data['shares'] == 3
        assert 'testing' in post_data['hashtags']
    
    def test_extract_post_data_handles_missing_elements(self):
        """Test extraction handles missing elements gracefully."""
        scraper = FacebookScraper()
        
        # Mock the container element with minimal data
        mock_container = Mock()
        mock_container.find_element.side_effect = Exception("Element not found")
        mock_container.find_elements.return_value = []
        
        # Extract data - should not raise exception
        post_data = scraper._extract_post_data_from_container(mock_container)
        
        # Should return None or handle gracefully
        assert post_data is None
    
    def test_extract_post_data_extracts_hashtags(self):
        """Test hashtag extraction from post content."""
        scraper = FacebookScraper()
        
        # Mock container with post containing hashtags
        mock_container = Mock()
        
        mock_link = Mock()
        mock_link.get_attribute.return_value = "https://facebook.com/user/posts/123"
        
        mock_author = Mock()
        mock_author.text = "Test User"
        mock_author_link = Mock()
        mock_author_link.get_attribute.return_value = "https://facebook.com/testuser"
        mock_author.find_element.return_value = mock_author_link
        
        mock_content = Mock()
        mock_content.text = "Testing #python #selenium #webscraping"
        
        mock_time = Mock()
        mock_time.get_attribute.return_value = "1 hour ago"
        
        # Mock engagement buttons
        mock_like = Mock()
        mock_like.get_attribute.return_value = "5 Likes"
        
        mock_comment = Mock()
        mock_comment.get_attribute.return_value = "2 Comments"
        
        mock_share = Mock()
        mock_share.get_attribute.return_value = "1 Share"
        
        def find_element_side_effect(by, selector):
            if selector == 'a[href*="/posts/"]':
                return mock_link
            elif selector == 'a[role="link"] strong':
                return mock_author
            elif selector == '[data-ad-preview="message"]':
                return mock_content
            elif selector == 'a[aria-label*="ago"]':
                return mock_time
            elif selector == '[aria-label*="Like"]':
                return mock_like
            elif selector == '[aria-label*="Comment"]':
                return mock_comment
            elif selector == '[aria-label*="Share"]':
                return mock_share
            else:
                raise Exception("Element not found")
        
        mock_container.find_element = Mock(side_effect=find_element_side_effect)
        mock_container.find_elements.return_value = []
        
        # Extract data
        post_data = scraper._extract_post_data_from_container(mock_container)
        
        # Verify hashtags
        assert post_data is not None
        assert 'python' in post_data['hashtags']
        assert 'selenium' in post_data['hashtags']
        assert 'webscraping' in post_data['hashtags']
        assert len(post_data['hashtags']) == 3


class TestFacebookScraperAuthentication:
    """Test FacebookScraper authentication methods."""
    
    @patch('scraper.scrapers.facebook.WebDriverWait')
    def test_authenticate_requires_driver_setup(self, mock_wait):
        """Test that authenticate requires driver to be set up first."""
        scraper = FacebookScraper(credentials={'username': 'test', 'password': 'pass'})
        
        # Without setting up driver, should raise an error
        with pytest.raises(Exception):
            scraper.authenticate()


class TestFacebookScraperIntegration:
    """Test FacebookScraper integration and workflow."""
    
    def test_scraper_can_be_used_as_context_manager(self):
        """Test that scraper can be used with 'with' statement."""
        with FacebookScraper() as scraper:
            assert scraper is not None
            assert isinstance(scraper, FacebookScraper)
    
    def test_scraper_repr(self):
        """Test string representation of scraper."""
        scraper = FacebookScraper(rate_limit=20, timeout=600)
        
        repr_str = repr(scraper)
        assert 'FacebookScraper' in repr_str
        assert 'rate_limit=20' in repr_str
        assert 'timeout=600' in repr_str


class TestFacebookScraperErrorHandling:
    """Test FacebookScraper error handling."""
    
    def test_initialization_with_invalid_rate_limit(self):
        """Test that invalid rate limit raises ValueError."""
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            FacebookScraper(rate_limit=0)
    
    def test_initialization_with_invalid_timeout(self):
        """Test that invalid timeout raises ValueError."""
        with pytest.raises(ValueError, match="timeout must be positive"):
            FacebookScraper(timeout=-1)
    
    def test_initialization_with_invalid_max_retries(self):
        """Test that invalid max_retries raises ValueError."""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            FacebookScraper(max_retries=-1)


class TestFacebookScraperConstants:
    """Test FacebookScraper constants and configuration."""
    
    def test_login_url_is_correct(self):
        """Test that LOGIN_URL is set correctly."""
        assert FacebookScraper.LOGIN_URL == "https://www.facebook.com/login"
    
    def test_base_url_is_correct(self):
        """Test that BASE_URL is set correctly."""
        assert FacebookScraper.BASE_URL == "https://www.facebook.com"
    
    def test_selectors_are_defined(self):
        """Test that all required selectors are defined."""
        selectors = FacebookScraper.SELECTORS
        
        assert 'email_input' in selectors
        assert 'password_input' in selectors
        assert 'login_button' in selectors
        assert 'post_container' in selectors
        assert 'post_content' in selectors
        assert 'post_author' in selectors


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
