"""
Platform-specific scraper implementations.
"""

from scraper.scrapers.base_scraper import (
    BaseScraper,
    ScraperError,
    AuthenticationError,
    NetworkError,
    TimeoutError
)
from scraper.scrapers.instagram import InstagramScraper
from scraper.scrapers.twitter import TwitterScraper
from scraper.scrapers.facebook import FacebookScraper
from scraper.scrapers.facebook_comments import FacebookCommentCrawler

__all__ = [
    'BaseScraper',
    'ScraperError',
    'AuthenticationError',
    'NetworkError',
    'TimeoutError',
    'InstagramScraper',
    'TwitterScraper',
    'FacebookScraper',
    'FacebookCommentCrawler'
]
