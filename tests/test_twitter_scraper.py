"""
Unit Tests for Twitter Scraper

Tests the TwitterScraper class functionality including:
- Initialization and configuration
- Post ID extraction
- Data extraction methods
- Error handling

Validates: Requirements 1.1, 1.2
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from scraper.scrapers.twitter import TwitterScraper
from scraper.scrapers.base_scraper import AuthenticationError


class TestTwitterScraperInitialization:
    """Test TwitterScraper initialization and configuration."""
    
    def test_initialization_with_defaults(self):
        """Test scraper initializes with default parameters."""
        scraper = TwitterScraper()
        
        assert scraper.rate_limit == 30
        assert scraper.timeout == 300
        assert scraper.headless is True
        assert scraper.max_retries == 5
        assert scraper.credentials == {}
    
    def test_initialization_with_credentials(self):
        """Test scraper initializes with provided credentials."""
        credentials = {'username': 'test_user', 'password': 'test_pass'}
        scraper = TwitterScraper(credentials=credentials)
        
        assert scraper.credentials == credentials
    
    def test_initialization_with_custom_parameters(self):
        """Test scraper initializes with custom parameters."""
        scraper = TwitterScraper(
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


class TestTwitterScraperHelperMethods:
    """Test TwitterScraper helper methods."""
    
    def test_extract_post_id_from_standard_url(self):
        """Test extracting tweet ID from standard Twitter URL."""
        scraper = TwitterScraper()
        
        url = "https://twitter.com/user/status/1234567890123456789"
        post_id = scraper._extract_post_id_from_url(url)
        
        assert post_id == "1234567890123456789"
    
    def test_extract_post_id_from_x_domain_url(self):
        """Test extracting tweet ID from x.com domain URL."""
        scraper = TwitterScraper()
        
        url = "https://x.com/user/status/9876543210987654321"
        post_id = scraper._extract_post_id_from_url(url)
        
        assert post_id == "9876543210987654321"
    
    def test_extract_post_id_from_malformed_url(self):
        """Test extracting post ID from malformed URL falls back gracefully."""
        scraper = TwitterScraper()
        
        url = "https://twitter.com/some/weird/path/"
        post_id = scraper._extract_post_id_from_url(url)
        
        # Should return a fallback ID starting with "tweet_"
        assert post_id.startswith("tweet_")


class TestTwitterScraperDataExtraction:
    """Test TwitterScraper data extraction methods."""
    
    def test_extract_tweet_data_from_article_with_complete_data(self):
        """Test extracting complete tweet data from article element."""
        scraper = TwitterScraper()
        
        # Mock the article element
        mock_article = Mock()
        
        # Mock tweet link
        mock_link = Mock()
        mock_link.get_attribute.return_value = "https://twitter.com/testuser/status/123456789"
        mock_article.find_element.side_effect = lambda by, selector: {
            'a[href*="/status/"]': mock_link,
        }.get(selector, Mock())
        
        # Mock author element
        mock_author = Mock()
        mock_author.text = "Test User\n@testuser"
        
        # Mock tweet text
        mock_text = Mock()
        mock_text.text = "This is a test tweet #testing"
        
        # Mock time element
        mock_time = Mock()
        mock_time.get_attribute.return_value = "2024-01-15T10:30:00.000Z"
        
        # Mock engagement buttons
        mock_like = Mock()
        mock_like.get_attribute.return_value = "5 Likes"
        
        mock_retweet = Mock()
        mock_retweet.get_attribute.return_value = "3 Retweets"
        
        mock_reply = Mock()
        mock_reply.get_attribute.return_value = "2 Replies"
        
        # Setup find_element to return appropriate mocks
        def find_element_side_effect(by, selector):
            selector_map = {
                '[data-testid="User-Name"]': mock_author,
                '[data-testid="tweetText"]': mock_text,
                'time': mock_time,
                '[data-testid="like"]': mock_like,
                '[data-testid="retweet"]': mock_retweet,
                '[data-testid="reply"]': mock_reply,
                'a[href*="/status/"]': mock_link,
            }
            return selector_map.get(selector, Mock())
        
        mock_article.find_element = Mock(side_effect=find_element_side_effect)
        mock_article.find_elements.return_value = []  # No media elements
        
        # Extract data
        tweet_data = scraper._extract_tweet_data_from_article(mock_article)
        
        # Verify extracted data
        assert tweet_data is not None
        assert tweet_data['post_id'] == "123456789"
        assert tweet_data['platform'] == 'twitter'
        assert tweet_data['author'] == 'testuser'
        assert tweet_data['content'] == "This is a test tweet #testing"
        assert tweet_data['likes'] == 5
        assert tweet_data['retweets'] == 3
        assert tweet_data['replies'] == 2
        assert 'testing' in tweet_data['hashtags']
    
    def test_extract_tweet_data_handles_missing_elements(self):
        """Test extraction handles missing elements gracefully."""
        scraper = TwitterScraper()
        
        # Mock the article element with minimal data
        mock_article = Mock()
        mock_article.find_element.side_effect = Exception("Element not found")
        mock_article.find_elements.return_value = []
        
        # Extract data - should not raise exception
        tweet_data = scraper._extract_tweet_data_from_article(mock_article)
        
        # Should return None or handle gracefully
        # The implementation logs errors and returns None
        assert tweet_data is None
    
    def test_extract_tweet_data_extracts_hashtags(self):
        """Test hashtag extraction from tweet content."""
        scraper = TwitterScraper()
        
        # Mock article with tweet containing hashtags
        mock_article = Mock()
        
        mock_link = Mock()
        mock_link.get_attribute.return_value = "https://twitter.com/user/status/123"
        
        mock_author = Mock()
        mock_author.text = "Test User\n@testuser"
        mock_author_link = Mock()
        mock_author_link.get_attribute.return_value = "https://twitter.com/testuser"
        mock_author.find_element.return_value = mock_author_link
        
        mock_text = Mock()
        mock_text.text = "Testing #python #selenium #webscraping"
        
        mock_time = Mock()
        mock_time.get_attribute.return_value = "2024-01-15T10:30:00.000Z"
        
        # Mock engagement buttons
        mock_like = Mock()
        mock_like.get_attribute.return_value = "5 Likes"
        
        mock_retweet = Mock()
        mock_retweet.get_attribute.return_value = "3 Retweets"
        
        mock_reply = Mock()
        mock_reply.get_attribute.return_value = "2 Replies"
        
        def find_element_side_effect(by, selector):
            if selector == 'a[href*="/status/"]':
                return mock_link
            elif selector == '[data-testid="User-Name"]':
                return mock_author
            elif selector == '[data-testid="tweetText"]':
                return mock_text
            elif selector == 'time':
                return mock_time
            elif selector == '[data-testid="like"]':
                return mock_like
            elif selector == '[data-testid="retweet"]':
                return mock_retweet
            elif selector == '[data-testid="reply"]':
                return mock_reply
            else:
                raise Exception("Element not found")
        
        mock_article.find_element = Mock(side_effect=find_element_side_effect)
        mock_article.find_elements.return_value = []
        
        # Extract data
        tweet_data = scraper._extract_tweet_data_from_article(mock_article)
        
        # Verify hashtags
        assert tweet_data is not None
        assert 'python' in tweet_data['hashtags']
        assert 'selenium' in tweet_data['hashtags']
        assert 'webscraping' in tweet_data['hashtags']
        assert len(tweet_data['hashtags']) == 3


class TestTwitterScraperAuthentication:
    """Test TwitterScraper authentication methods."""
    
    @patch('scraper.scrapers.twitter.WebDriverWait')
    def test_authenticate_requires_driver_setup(self, mock_wait):
        """Test that authenticate requires driver to be set up first."""
        scraper = TwitterScraper(credentials={'username': 'test', 'password': 'pass'})
        
        # Without setting up driver, should raise an error
        with pytest.raises(Exception):
            scraper.authenticate()


class TestTwitterScraperIntegration:
    """Test TwitterScraper integration and workflow."""
    
    def test_scraper_can_be_used_as_context_manager(self):
        """Test that scraper can be used with 'with' statement."""
        with TwitterScraper() as scraper:
            assert scraper is not None
            assert isinstance(scraper, TwitterScraper)
    
    def test_scraper_repr(self):
        """Test string representation of scraper."""
        scraper = TwitterScraper(rate_limit=20, timeout=600)
        
        repr_str = repr(scraper)
        assert 'TwitterScraper' in repr_str
        assert 'rate_limit=20' in repr_str
        assert 'timeout=600' in repr_str


class TestTwitterScraperErrorHandling:
    """Test TwitterScraper error handling."""
    
    def test_initialization_with_invalid_rate_limit(self):
        """Test that invalid rate limit raises ValueError."""
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            TwitterScraper(rate_limit=0)
    
    def test_initialization_with_invalid_timeout(self):
        """Test that invalid timeout raises ValueError."""
        with pytest.raises(ValueError, match="timeout must be positive"):
            TwitterScraper(timeout=-1)
    
    def test_initialization_with_invalid_max_retries(self):
        """Test that invalid max_retries raises ValueError."""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            TwitterScraper(max_retries=-1)
