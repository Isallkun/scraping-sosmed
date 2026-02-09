"""
Unit tests for Instagram scraper implementation.

Tests the InstagramScraper class methods and functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from scraper.scrapers.instagram import InstagramScraper
from scraper.scrapers.base_scraper import AuthenticationError, ScraperError


class TestInstagramScraperInitialization:
    """Test Instagram scraper initialization."""
    
    def test_initialization_with_defaults(self):
        """Test scraper initializes with default parameters."""
        scraper = InstagramScraper()
        
        assert scraper.rate_limit == 30
        assert scraper.timeout == 300
        assert scraper.headless is True
        assert scraper.max_retries == 5
        assert scraper.credentials == {}
    
    def test_initialization_with_credentials(self):
        """Test scraper initializes with provided credentials."""
        credentials = {'username': 'test_user', 'password': 'test_pass'}
        scraper = InstagramScraper(credentials=credentials)
        
        assert scraper.credentials == credentials
    
    def test_initialization_with_custom_parameters(self):
        """Test scraper initializes with custom parameters."""
        scraper = InstagramScraper(
            rate_limit=20,
            timeout=600,
            headless=False,
            max_retries=3
        )
        
        assert scraper.rate_limit == 20
        assert scraper.timeout == 600
        assert scraper.headless is False
        assert scraper.max_retries == 3


class TestInstagramScraperURLParsing:
    """Test URL parsing and post ID extraction."""
    
    def test_extract_post_id_from_standard_url(self):
        """Test extracting post ID from standard Instagram URL."""
        scraper = InstagramScraper()
        url = "https://www.instagram.com/p/ABC123xyz/"
        
        post_id = scraper._extract_post_id_from_url(url)
        
        assert post_id == "ABC123xyz"
    
    def test_extract_post_id_from_url_without_trailing_slash(self):
        """Test extracting post ID from URL without trailing slash."""
        scraper = InstagramScraper()
        url = "https://www.instagram.com/p/XYZ789abc"
        
        post_id = scraper._extract_post_id_from_url(url)
        
        assert post_id == "XYZ789abc"
    
    def test_extract_post_id_from_malformed_url(self):
        """Test extracting post ID from malformed URL falls back gracefully."""
        scraper = InstagramScraper()
        url = "https://www.instagram.com/some/weird/path/"
        
        post_id = scraper._extract_post_id_from_url(url)
        
        # Should return something (fallback behavior)
        assert post_id is not None
        assert len(post_id) > 0


class TestInstagramScraperDataExtraction:
    """Test data extraction from post elements."""
    
    def test_extract_post_data_from_feed_with_complete_data(self):
        """Test extracting complete post data from feed element."""
        scraper = InstagramScraper()
        
        # Mock the link element and article
        mock_link = Mock()
        mock_article = Mock()
        mock_link.find_element.return_value = mock_article
        
        # Mock author
        mock_author_link = Mock()
        mock_author_link.text = "test_user"
        mock_author_link.get_attribute.return_value = "https://www.instagram.com/test_user/"
        mock_article.find_element.return_value = mock_author_link
        
        # Mock caption
        mock_caption = Mock()
        mock_caption.text = "Test caption with #hashtag"
        mock_article.find_elements.return_value = [mock_caption]
        
        # Mock timestamp
        mock_time = Mock()
        mock_time.get_attribute.return_value = "2024-01-15T10:30:00Z"
        
        # Setup find_element to return different mocks based on selector
        def find_element_side_effect(by, selector):
            if 'author' in str(selector) or 'header' in str(selector):
                return mock_author_link
            elif 'time' in str(selector):
                return mock_time
            return Mock()
        
        def find_elements_side_effect(by, selector=None):
            if selector is None:
                # Called with just tag name
                if by == 'h1':
                    return [mock_caption]
                elif by == 'video':
                    return []
                elif by == 'img':
                    return [Mock()]
            else:
                # Called with CSS selector
                if 'span' in str(selector) or 'h1' in str(selector):
                    return [mock_caption]
                elif 'button span' in str(selector):
                    mock_likes = Mock()
                    mock_likes.text = "150"
                    return [mock_likes]
                elif 'video' in str(selector):
                    return []
                elif 'img' in str(selector):
                    return [Mock()]
            return []
        
        mock_article.find_element.side_effect = find_element_side_effect
        mock_article.find_elements.side_effect = find_elements_side_effect
        
        post_id = "ABC123"
        post_url = "https://www.instagram.com/p/ABC123/"
        
        result = scraper._extract_post_data_from_feed(mock_link, post_id, post_url)
        
        assert result is not None
        assert result['post_id'] == post_id
        assert result['platform'] == 'instagram'
        assert result['author'] == 'test_user'
        assert result['url'] == post_url
        assert 'timestamp' in result
        assert 'hashtag' in result['hashtags']
    
    def test_extract_post_data_handles_missing_elements(self):
        """Test extraction handles missing elements gracefully."""
        scraper = InstagramScraper()
        
        # Mock the link element and article
        mock_link = Mock()
        mock_article = Mock()
        mock_link.find_element.return_value = mock_article
        
        # Make all find_element calls raise NoSuchElementException
        mock_article.find_element.side_effect = NoSuchElementException("Element not found")
        mock_article.find_elements.return_value = []
        
        post_id = "ABC123"
        post_url = "https://www.instagram.com/p/ABC123/"
        
        result = scraper._extract_post_data_from_feed(mock_link, post_id, post_url)
        
        # Should still return a result with default values
        assert result is not None
        assert result['post_id'] == post_id
        assert result['platform'] == 'instagram'
        assert result['author'] == 'unknown'
        assert result['content'] == ''
        assert result['likes'] == 0
        assert result['comments_count'] == 0
    
    def test_extract_post_data_extracts_hashtags(self):
        """Test hashtag extraction from post content."""
        scraper = InstagramScraper()
        
        # Mock the link element and article
        mock_link = Mock()
        mock_article = Mock()
        mock_link.find_element.return_value = mock_article
        
        # Mock caption with multiple hashtags
        mock_caption = Mock()
        mock_caption.text = "Great photo! #travel #photography #nature"
        
        def find_elements_side_effect(by, selector=None):
            if selector is None and by == 'h1':
                return [mock_caption]
            elif 'span' in str(selector):
                return [mock_caption]
            return []
        
        mock_article.find_element.side_effect = NoSuchElementException()
        mock_article.find_elements.side_effect = find_elements_side_effect
        
        post_id = "ABC123"
        post_url = "https://www.instagram.com/p/ABC123/"
        
        result = scraper._extract_post_data_from_feed(mock_link, post_id, post_url)
        
        assert result is not None
        assert 'travel' in result['hashtags']
        assert 'photography' in result['hashtags']
        assert 'nature' in result['hashtags']
        assert len(result['hashtags']) == 3


class TestInstagramScraperAuthentication:
    """Test authentication flow."""
    
    @patch('scraper.scrapers.instagram.WebDriverWait')
    def test_authenticate_requires_driver_setup(self, mock_wait):
        """Test that authenticate requires driver to be set up first."""
        scraper = InstagramScraper(credentials={'username': 'test', 'password': 'pass'})
        
        # Without setting up driver, should raise an AuthenticationError
        with pytest.raises(AuthenticationError):
            scraper.authenticate()
    
    def test_extract_post_data_not_implemented(self):
        """Test that extract_post_data raises NotImplementedError."""
        scraper = InstagramScraper()
        
        with pytest.raises(NotImplementedError):
            scraper.extract_post_data(Mock())


class TestInstagramScraperConstants:
    """Test scraper constants and configuration."""
    
    def test_login_url_is_correct(self):
        """Test that LOGIN_URL is set correctly."""
        assert InstagramScraper.LOGIN_URL == "https://www.instagram.com/accounts/login/"
    
    def test_base_url_is_correct(self):
        """Test that BASE_URL is set correctly."""
        assert InstagramScraper.BASE_URL == "https://www.instagram.com"
    
    def test_selectors_are_defined(self):
        """Test that all required selectors are defined."""
        selectors = InstagramScraper.SELECTORS
        
        assert 'username_input' in selectors
        assert 'password_input' in selectors
        assert 'login_button' in selectors
        assert 'article' in selectors
        assert 'post_link' in selectors
        assert 'post_author' in selectors


class TestInstagramScraperIntegration:
    """Integration tests for Instagram scraper (without actual web requests)."""
    
    def test_scraper_can_be_used_as_context_manager(self):
        """Test that scraper can be used with 'with' statement."""
        with InstagramScraper() as scraper:
            assert scraper is not None
            assert isinstance(scraper, InstagramScraper)
    
    def test_scraper_repr(self):
        """Test string representation of scraper."""
        scraper = InstagramScraper(rate_limit=20, timeout=600)
        repr_str = repr(scraper)
        
        assert 'InstagramScraper' in repr_str
        assert 'rate_limit=20' in repr_str
        assert 'timeout=600' in repr_str


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
