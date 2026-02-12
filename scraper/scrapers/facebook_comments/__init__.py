"""
Facebook Comment Crawler Module

Playwright-based Facebook comment crawler integrated from crawling-facebook project.
Provides advanced comment extraction capabilities including:
- Single post comment crawling
- Profile-based post discovery and comment crawling
- Batch processing from URL/profile files
- Export to CSV, Excel, and JSON formats

Usage:
    from scraper.scrapers.facebook_comments import FacebookCommentCrawler

    crawler = FacebookCommentCrawler()
    comments = crawler.crawl_comments(post_url="https://facebook.com/user/posts/123")
"""

from scraper.scrapers.facebook_comments.crawler import FacebookCommentCrawler

__all__ = ['FacebookCommentCrawler']
