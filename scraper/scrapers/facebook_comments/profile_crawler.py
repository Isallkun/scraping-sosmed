"""Profile crawler to discover posts from Facebook user profiles"""

from typing import List, Optional
from playwright.sync_api import Page

from scraper.utils.logger import get_logger
from scraper.scrapers.facebook_comments.config import FBCommentConfig
from scraper.scrapers.facebook_comments.utils import random_delay, human_like_scroll, extract_username_from_url

logger = get_logger('scraper.facebook_comments.profile')


class ProfileCrawler:
    """Crawl Facebook profile to discover post URLs"""

    def __init__(self, page: Page):
        self.page = page
        self.max_posts = FBCommentConfig.MAX_POSTS_PER_PROFILE
        self.scroll_limit = FBCommentConfig.PROFILE_SCROLL_LIMIT
        self.target_username = None

    def get_posts_from_profile(
        self,
        profile_url: str,
        max_posts: Optional[int] = None
    ) -> List[str]:
        """
        Get list of post URLs from a Facebook profile.

        Args:
            profile_url: URL of the Facebook profile
            max_posts: Maximum number of posts to collect

        Returns:
            List of post URLs
        """
        max_posts = max_posts or self.max_posts
        logger.info(f"Crawling profile: {profile_url}")
        logger.info(f"Target: {max_posts} posts")

        try:
            self.target_username = self._extract_username_from_url(profile_url)
            logger.info(f"Target username: {self.target_username}")

            self.page.goto(profile_url, timeout=FBCommentConfig.REQUEST_TIMEOUT)
            random_delay(3, 5)

            post_urls = set()
            scroll_count = 0
            no_new_posts_count = 0

            while len(post_urls) < max_posts and scroll_count < self.scroll_limit:
                previous_count = len(post_urls)
                new_urls = self._extract_post_urls()
                post_urls.update(new_urls)

                logger.debug(f"Found {len(post_urls)} posts so far (scroll {scroll_count + 1}/{self.scroll_limit})")

                if len(post_urls) >= max_posts:
                    logger.info(f"Reached target of {max_posts} posts")
                    break

                if len(post_urls) == previous_count:
                    no_new_posts_count += 1
                    if no_new_posts_count >= 3:
                        logger.info("No new posts found after 3 scrolls, stopping...")
                        break
                else:
                    no_new_posts_count = 0

                current_url = self.page.url
                if 'facebook.com/' not in current_url or current_url == 'https://www.facebook.com/' or '/home' in current_url:
                    logger.warning(f"Not on profile page anymore (URL: {current_url}), stopping...")
                    break

                human_like_scroll(self.page, scroll_amount=500)
                random_delay(2, 4)
                scroll_count += 1

            post_urls_list = list(post_urls)[:max_posts]
            logger.info(f"Collected {len(post_urls_list)} post URLs from profile")
            return post_urls_list

        except Exception as e:
            logger.error(f"Error crawling profile: {e}")
            return []

    def _extract_username_from_url(self, url: str) -> str:
        """Extract username from Facebook profile URL"""
        try:
            if '/profile.php?' in url:
                if 'id=' in url:
                    return url.split('id=')[-1].split('&')[0]
            else:
                parts = url.rstrip('/').split('/')
                for part in reversed(parts):
                    if part and part not in ['www.facebook.com', 'facebook.com', 'http:', 'https:']:
                        return part
            return ""
        except Exception as e:
            logger.error(f"Error extracting username from URL: {e}")
            return ""

    def _extract_post_urls(self) -> List[str]:
        """Extract post URLs from current page"""
        post_urls = []

        try:
            link_selectors = [
                'a[href*="/posts/"]',
                'a[href*="/story.php"]',
                'a[href*="/permalink.php"]',
                'a[href*="/videos/"]',
                'a[href*="/reel/"]',
                'a[href*="/photo"]'
            ]

            for selector in link_selectors:
                elements = self.page.query_selector_all(selector)
                for element in elements:
                    try:
                        href = element.get_attribute('href')
                        if href and self._is_valid_post_url(href):
                            if href.startswith('/'):
                                href = f"https://www.facebook.com{href}"
                            href = href.split('?')[0]
                            post_urls.append(href)
                    except Exception:
                        continue

            return list(set(post_urls))

        except Exception as e:
            logger.error(f"Error extracting post URLs: {e}")
            return []

    def _is_valid_post_url(self, url: str) -> bool:
        """Check if URL is a valid Facebook post URL"""
        try:
            invalid_patterns = [
                '/about', '/friends', '/photos', '/videos/?',
                '/groups', '/events', 'photo.php?fbid',
                '/reels?', '/watch'
            ]

            for pattern in invalid_patterns:
                if pattern in url:
                    return False

            if 'facebook.com' not in url and not url.startswith('/'):
                return False

            valid_patterns = [
                '/posts/', '/story.php?', '/permalink.php?',
                '/videos/', '/reel/', '/photo.php?'
            ]

            return any(pattern in url for pattern in valid_patterns)

        except Exception:
            return False

    def get_posts_from_username(
        self,
        username: str,
        max_posts: Optional[int] = None
    ) -> List[str]:
        """
        Get posts from a Facebook username.

        Args:
            username: Facebook username
            max_posts: Maximum number of posts to collect

        Returns:
            List of post URLs
        """
        if username.startswith('http'):
            username = extract_username_from_url(username)

        profile_url = f"https://www.facebook.com/{username}"
        return self.get_posts_from_profile(profile_url, max_posts)
