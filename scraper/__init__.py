"""
Social Media Scraper Module

This module provides functionality for scraping data from social media platforms
including Instagram, Twitter, and Facebook using Selenium WebDriver.

Main components:
- config: Configuration management from environment variables
- main_scraper: CLI interface for scraping operations
- scrapers: Platform-specific scraper implementations
- utils: Utility modules (logging, rate limiting, anti-detection)
"""

__version__ = "0.1.0"

# Import main components for easy access
from scraper.config import ScraperConfig, get_config, ConfigurationError

__all__ = [
    'ScraperConfig',
    'get_config',
    'ConfigurationError',
    '__version__',
]
