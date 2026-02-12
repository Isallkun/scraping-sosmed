"""
Facebook Comment Crawler - Main orchestrator

High-level class that combines authentication, comment extraction, profile crawling,
and data export into a unified interface for crawling Facebook comments.

Integrated from the crawling-facebook project into scraping-sosmed.
"""

import sys
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright

from scraper.utils.logger import get_logger
from scraper.scrapers.facebook_comments.config import FBCommentConfig
from scraper.scrapers.facebook_comments.auth import FacebookAuth
from scraper.scrapers.facebook_comments.comment_extractor import CommentExtractor
from scraper.scrapers.facebook_comments.profile_crawler import ProfileCrawler
from scraper.scrapers.facebook_comments.exporters import CSVExporter, JSONExporter
from scraper.scrapers.facebook_comments.utils import (
    validate_url,
    extract_username_from_url,
    read_urls_from_file,
)

logger = get_logger('scraper.facebook_comments')


class FacebookCommentCrawler:
    """
    High-level Facebook comment crawler using Playwright.

    Provides methods to crawl comments from:
    - Single Facebook post URL
    - Facebook profile (discovers posts then crawls comments)
    - Batch of URLs from a file
    - Batch of profiles from a file

    Results can be exported to CSV, Excel, or JSON format.

    Example:
        crawler = FacebookCommentCrawler()

        # Crawl comments from a single post
        result = crawler.crawl_comments(post_url="https://facebook.com/user/posts/123")

        # Crawl comments from a profile
        result = crawler.crawl_from_profile(
            profile_url="https://facebook.com/username",
            max_posts=10
        )

        # Crawl with custom export
        result = crawler.crawl_comments(
            post_url="https://facebook.com/user/posts/123",
            export_format="json",
            export_mode="single"
        )
    """

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        headless: Optional[bool] = None,
        export_format: Optional[str] = None,
        export_mode: Optional[str] = None,
    ):
        """
        Initialize Facebook Comment Crawler.

        Args:
            email: Facebook email (defaults to env var FB_COMMENT_EMAIL or FACEBOOK_USERNAME)
            password: Facebook password (defaults to env var FB_COMMENT_PASSWORD or FACEBOOK_PASSWORD)
            headless: Run browser in headless mode (defaults to env var FB_COMMENT_HEADLESS)
            export_format: Export format: 'csv', 'excel', 'json', or 'both' (defaults to env var)
            export_mode: Export mode: 'single' or 'per-post' (defaults to env var)
        """
        self.email = email
        self.password = password
        self.headless = headless if headless is not None else FBCommentConfig.HEADLESS
        self.export_format = export_format or FBCommentConfig.EXPORT_FORMAT
        self.export_mode = export_mode or FBCommentConfig.EXPORT_MODE

    def crawl_comments(
        self,
        post_url: str,
        max_comments: Optional[int] = None,
        export_format: Optional[str] = None,
        export_mode: Optional[str] = None,
        auto_export: bool = True,
    ) -> Dict[str, Any]:
        """
        Crawl comments from a single Facebook post.

        Args:
            post_url: URL of the Facebook post
            max_comments: Maximum number of comments to crawl (None for all)
            export_format: Override export format for this call
            export_mode: Override export mode for this call
            auto_export: Whether to auto-export results to file

        Returns:
            Dictionary with 'comments' list and 'exported_files' list
        """
        return self._run_crawl(
            post_urls=[post_url],
            max_comments=max_comments,
            export_format=export_format or self.export_format,
            export_mode=export_mode or self.export_mode,
            auto_export=auto_export,
        )

    def crawl_from_profile(
        self,
        profile_url: Optional[str] = None,
        username: Optional[str] = None,
        max_posts: Optional[int] = None,
        max_comments: Optional[int] = None,
        export_format: Optional[str] = None,
        export_mode: Optional[str] = None,
        auto_export: bool = True,
    ) -> Dict[str, Any]:
        """
        Crawl comments from all posts of a Facebook profile.

        Args:
            profile_url: Facebook profile URL
            username: Facebook username (alternative to profile_url)
            max_posts: Maximum posts to crawl from profile
            max_comments: Maximum comments per post
            export_format: Override export format
            export_mode: Override export mode
            auto_export: Whether to auto-export results

        Returns:
            Dictionary with 'comments' list and 'exported_files' list
        """
        return self._run_crawl(
            profile_url=profile_url,
            username=username,
            max_posts=max_posts,
            max_comments=max_comments,
            export_format=export_format or self.export_format,
            export_mode=export_mode or self.export_mode,
            auto_export=auto_export,
        )

    def crawl_from_file(
        self,
        urls_file: Optional[str] = None,
        profiles_file: Optional[str] = None,
        max_posts: Optional[int] = None,
        max_comments: Optional[int] = None,
        export_format: Optional[str] = None,
        export_mode: Optional[str] = None,
        auto_export: bool = True,
    ) -> Dict[str, Any]:
        """
        Crawl comments from URLs or profiles listed in a file.

        Args:
            urls_file: Path to file with post URLs (one per line)
            profiles_file: Path to file with profile URLs/usernames (one per line)
            max_posts: Maximum posts per profile
            max_comments: Maximum comments per post
            export_format: Override export format
            export_mode: Override export mode
            auto_export: Whether to auto-export results

        Returns:
            Dictionary with 'comments' list and 'exported_files' list
        """
        post_urls = []
        profiles = []

        if urls_file:
            post_urls = read_urls_from_file(urls_file)
        if profiles_file:
            profiles = read_urls_from_file(profiles_file)

        return self._run_crawl(
            post_urls=post_urls if post_urls else None,
            profiles=profiles if profiles else None,
            max_posts=max_posts,
            max_comments=max_comments,
            export_format=export_format or self.export_format,
            export_mode=export_mode or self.export_mode,
            auto_export=auto_export,
        )

    def _run_crawl(
        self,
        post_urls: Optional[List[str]] = None,
        profile_url: Optional[str] = None,
        username: Optional[str] = None,
        profiles: Optional[List[str]] = None,
        max_posts: Optional[int] = None,
        max_comments: Optional[int] = None,
        export_format: str = "csv",
        export_mode: str = "single",
        auto_export: bool = True,
    ) -> Dict[str, Any]:
        """Internal method to run the full crawl pipeline."""

        all_comments = []
        exported_files = []
        username_for_filename = None

        # Setup exporters
        csv_exporter = None
        json_exporter = None

        if export_format in ['csv', 'both']:
            csv_exporter = CSVExporter(export_mode=export_mode, export_format='csv')
        if export_format in ['json', 'both']:
            json_exporter = JSONExporter(export_mode=export_mode, pretty=True)
        if export_format == 'excel':
            csv_exporter = CSVExporter(export_mode=export_mode, export_format='excel')

        # Determine username for filename
        if profile_url:
            username_for_filename = extract_username_from_url(profile_url)
        elif username:
            username_for_filename = username

        try:
            with sync_playwright() as p:
                logger.info(f"Launching browser (headless={self.headless})...")
                browser = p.chromium.launch(headless=self.headless)

                # Authenticate
                auth = FacebookAuth(email=self.email, password=self.password)
                page = auth.login(browser)

                # Resolve post URLs from profile if needed
                if post_urls is None:
                    post_urls = []

                if profile_url or username:
                    profile_crawler = ProfileCrawler(page)
                    if username and not profile_url:
                        urls = profile_crawler.get_posts_from_username(
                            username,
                            max_posts=max_posts or FBCommentConfig.MAX_POSTS_PER_PROFILE
                        )
                    else:
                        urls = profile_crawler.get_posts_from_profile(
                            profile_url,
                            max_posts=max_posts or FBCommentConfig.MAX_POSTS_PER_PROFILE
                        )
                    post_urls.extend(urls)

                if profiles:
                    profile_crawler = ProfileCrawler(page)
                    for profile in profiles:
                        profile_username = extract_username_from_url(profile) if 'http' in profile else profile
                        urls = profile_crawler.get_posts_from_username(
                            profile_username,
                            max_posts=max_posts or FBCommentConfig.MAX_POSTS_PER_PROFILE
                        )
                        post_urls.extend(urls)

                if not post_urls:
                    logger.error("No posts to crawl!")
                    return {'comments': [], 'exported_files': [], 'stats': {}}

                logger.info(f"Total posts to crawl: {len(post_urls)}")

                # Crawl comments
                comment_crawler = CommentExtractor(page)

                for idx, post_url in enumerate(post_urls, 1):
                    logger.info(f"Post {idx}/{len(post_urls)}: {post_url}")

                    try:
                        comments = comment_crawler.crawl_post_comments(
                            post_url,
                            max_comments=max_comments
                        )

                        if comments:
                            all_comments.extend(comments)
                            if csv_exporter:
                                csv_exporter.add_comments(comments)
                            if json_exporter:
                                json_exporter.add_comments(comments)
                            logger.info(f"Collected {len(comments)} comments")
                        else:
                            logger.warning("No comments found")

                    except Exception as e:
                        logger.error(f"Error crawling post: {e}")
                        continue

                # Export results
                if auto_export:
                    if csv_exporter:
                        files = csv_exporter.export(username=username_for_filename)
                        exported_files.extend(files)
                    if json_exporter:
                        files = json_exporter.export(username=username_for_filename)
                        exported_files.extend(files)

                # Get stats
                active_exporter = csv_exporter or json_exporter
                stats = active_exporter.get_stats() if active_exporter else {}

                # Cleanup
                auth.close()
                browser.close()

                logger.info("Crawling completed successfully!")

        except KeyboardInterrupt:
            logger.warning("Crawling interrupted by user")
            if csv_exporter:
                exported_files.extend(csv_exporter.export(username=username_for_filename))
            if json_exporter:
                exported_files.extend(json_exporter.export(username=username_for_filename))
            stats = {}

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            stats = {}

        return {
            'comments': all_comments,
            'exported_files': exported_files,
            'stats': stats
        }
