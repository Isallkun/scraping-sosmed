"""Core comment extraction for Facebook posts using Playwright"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.sync_api import Page

from scraper.utils.logger import get_logger
from scraper.scrapers.facebook_comments.config import FBCommentConfig
from scraper.scrapers.facebook_comments.utils import random_delay, human_like_scroll

logger = get_logger('scraper.facebook_comments.extractor')


class CommentExtractor:
    """Extract comments from Facebook posts using Playwright"""

    def __init__(self, page: Page):
        self.page = page

    def crawl_post_comments(
        self,
        post_url: str,
        max_comments: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl all comments from a Facebook post.

        Args:
            post_url: URL of the Facebook post
            max_comments: Maximum number of comments to crawl (None for all)

        Returns:
            List of comment dictionaries
        """
        logger.info(f"Crawling comments from: {post_url}")

        try:
            self.page.goto(post_url, timeout=FBCommentConfig.REQUEST_TIMEOUT)
            random_delay(3, 5)

            post_info = self._extract_post_info()
            self._expand_all_comments(max_comments)
            comments = self._extract_comments(post_info)

            logger.info(f"Extracted {len(comments)} comments from post")
            return comments

        except Exception as e:
            logger.error(f"Error crawling post {post_url}: {e}")
            return []

    def _extract_post_info(self) -> Dict[str, Any]:
        """Extract basic post information"""
        post_info = {
            'post_url': self.page.url,
            'post_author': '',
            'post_content': '',
            'post_timestamp': ''
        }

        try:
            author_selectors = ['h2 a', 'h3 a', '[data-ad-preview="message"] a', 'a[role="link"]']
            for selector in author_selectors:
                element = self.page.query_selector(selector)
                if element:
                    post_info['post_author'] = element.text_content().strip()
                    if post_info['post_author']:
                        break

            content_selectors = [
                '[data-ad-preview="message"]',
                'div[data-ad-comet-preview="message"]',
                '[dir="auto"]'
            ]
            for selector in content_selectors:
                elements = self.page.query_selector_all(selector)
                for element in elements:
                    text = element.text_content().strip()
                    if text and len(text) > len(post_info['post_content']):
                        post_info['post_content'] = text
                        break
                if post_info['post_content']:
                    break

            if len(post_info['post_content']) > 500:
                post_info['post_content'] = post_info['post_content'][:500] + '...'

        except Exception as e:
            logger.warning(f"Could not extract post info: {e}")

        return post_info

    def _open_comment_section(self) -> bool:
        """Open comment section if it's collapsed/hidden"""
        try:
            comment_button_selectors = [
                'text=/View.*comment/i',
                'text=/Lihat.*komentar/i',
                '[aria-label*="comment"]',
                '[aria-label*="Comment"]',
                '[aria-label*="Komentar"]',
                'div[role="button"]:has-text("Comment")',
                'div[role="button"]:has-text("Komentar")'
            ]

            for selector in comment_button_selectors:
                try:
                    button = self.page.wait_for_selector(selector, timeout=3000)
                    if button and button.is_visible():
                        logger.info(f"Clicking comment button: {selector}")
                        button.click()
                        random_delay(2, 3)
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            logger.warning(f"Error opening comment section: {e}")
            return False

    def _expand_all_comments(self, max_comments: Optional[int] = None) -> None:
        """Expand all comments and replies"""
        logger.info("Expanding comments...")

        try:
            self._open_comment_section()
            random_delay(1, 2)

            scroll_attempts = 0
            max_scrolls = FBCommentConfig.MAX_SCROLL_ATTEMPTS

            while scroll_attempts < max_scrolls:
                human_like_scroll(self.page, scroll_amount=600)
                random_delay(2, 3)

                more_comments_clicked = self._click_view_more_buttons()
                scroll_attempts += 1

                if max_comments:
                    current_count = self._count_visible_comments()
                    if current_count >= max_comments:
                        logger.info(f"Reached target of {max_comments} comments")
                        break

                if not more_comments_clicked and scroll_attempts > 5:
                    logger.info("No more comments to load")
                    break

            self._expand_all_replies()
            self._expand_see_more_in_comments()

        except Exception as e:
            logger.warning(f"Error expanding comments: {e}")

    def _click_view_more_buttons(self) -> bool:
        """Click all 'View more comments' type buttons"""
        clicked = False

        try:
            selectors = [
                'text=/View more comments/i',
                'text=/Lihat komentar lainnya/i',
                'text=/View previous comments/i',
                'text=/Lihat komentar sebelumnya/i',
                '[aria-label*="more comment"]',
                '[aria-label*="komentar lainnya"]'
            ]

            for selector in selectors:
                try:
                    buttons = self.page.query_selector_all(selector)
                    for button in buttons:
                        try:
                            if button.is_visible():
                                button.click()
                                clicked = True
                                random_delay(1, 2)
                        except Exception:
                            continue
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"Error clicking view more buttons: {e}")

        return clicked

    def _expand_all_replies(self) -> None:
        """Expand all reply threads"""
        logger.info("Expanding reply threads...")

        try:
            selectors = [
                'text=/View.*repl/i',
                'text=/Lihat.*balas/i',
                'text=/\\d+ repl/i',
                'text=/\\d+ balas/i',
                '[aria-label*="repl"]',
                '[aria-label*="balas"]'
            ]

            for selector in selectors:
                try:
                    buttons = self.page.query_selector_all(selector)
                    for button in buttons[:50]:
                        try:
                            if button.is_visible():
                                button.scroll_into_view_if_needed()
                                random_delay(0.5, 1)
                                button.click()
                                random_delay(1, 2)
                        except Exception:
                            continue
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"Error expanding replies: {e}")

    def _expand_see_more_in_comments(self) -> None:
        """Click 'See more'/'Lihat selengkapnya' buttons to expand truncated comment text"""
        logger.info("Expanding truncated comments (See more buttons)...")

        try:
            see_more_selectors = [
                'text=/See more/i',
                'text=/Lihat selengkapnya/i',
                'div[role="button"]:has-text("See more")',
                'div[role="button"]:has-text("Lihat selengkapnya")',
            ]

            expanded_count = 0

            for selector in see_more_selectors:
                try:
                    buttons = self.page.query_selector_all(selector)
                    for button in buttons:
                        try:
                            if button.is_visible():
                                button_text = button.text_content().strip()
                                if any(text in button_text.lower() for text in ['see more', 'lihat selengkapnya']):
                                    button.scroll_into_view_if_needed()
                                    random_delay(0.3, 0.6)
                                    button.click()
                                    expanded_count += 1
                                    random_delay(0.5, 1)
                        except Exception:
                            continue
                except Exception:
                    continue

            logger.info(f"Expanded {expanded_count} truncated comments")

        except Exception as e:
            logger.warning(f"Error expanding see more buttons: {e}")

    def _count_visible_comments(self) -> int:
        """Count currently visible comments"""
        try:
            comment_selectors = [
                '[role="article"]',
                'div[aria-label*="Comment"]',
                'div[aria-label*="Komentar"]'
            ]

            for selector in comment_selectors:
                comments = self.page.query_selector_all(selector)
                if comments:
                    return len(comments)

            return 0
        except Exception:
            return 0

    def _extract_comments(self, post_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all visible comments"""
        logger.info("Extracting comment data...")
        comments = []

        try:
            random_delay(1, 2)

            comment_selectors = [
                'div[aria-label*="Comment by"]',
                'div[aria-label*="Komentar oleh"]',
                'div[role="article"] div[dir="auto"]',
                '[role="article"]'
            ]

            comment_elements = []
            for selector in comment_selectors:
                elements = self.page.query_selector_all(selector)
                if elements:
                    comment_elements = elements
                    break

            logger.info(f"Found {len(comment_elements)} potential comment elements")

            for idx, element in enumerate(comment_elements):
                try:
                    comment_data = self._extract_single_comment(element, post_info)
                    if comment_data:
                        comment_data['comment_id'] = f"comment_{idx}"
                        comments.append(comment_data)
                except Exception as e:
                    logger.debug(f"Error extracting comment {idx}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting comments: {e}")

        return comments

    def _extract_single_comment(
        self,
        element,
        post_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract data from a single comment element"""
        try:
            author_name = ""
            author_url = ""

            author_selectors = [
                'a[role="link"]',
                'a[href*="/user/"]',
                'a[href*="/profile"]',
                'a[aria-label]',
                'span[dir="auto"] a',
                'h4 a',
                'strong a'
            ]

            for selector in author_selectors:
                try:
                    author_link = element.query_selector(selector)
                    if author_link:
                        text = author_link.text_content().strip()
                        if text and len(text) > 0:
                            author_name = text
                            author_url = author_link.get_attribute('href') or ""
                            break
                except Exception:
                    continue

            if not author_name:
                try:
                    all_links = element.query_selector_all('a')
                    for link in all_links:
                        text = link.text_content().strip()
                        if text and len(text) > 2 and text not in ['Like', 'Reply', 'Suka', 'Balas']:
                            author_name = text
                            author_url = link.get_attribute('href') or ""
                            break
                except Exception:
                    pass

            # Extract comment text
            comment_text = ""

            text_elements = element.query_selector_all('div[dir="auto"], span[dir="auto"]')
            for text_elem in text_elements:
                text = text_elem.text_content().strip()
                if text and len(text) > 5:
                    if text not in [author_name, 'Like', 'Reply', 'Suka', 'Balas', 'Komentar', 'Comment']:
                        if len(text) > len(comment_text):
                            comment_text = text

            if not comment_text:
                full_text = element.text_content().strip()
                for noise in [author_name, 'Like', 'Reply', 'Suka', 'Balas', '\u00b7', 'Just now', 'yang lalu']:
                    full_text = full_text.replace(noise, '')
                comment_text = full_text.strip()

            # Remove URLs from comment text
            if comment_text:
                comment_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', comment_text)
                comment_text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', comment_text)
                comment_text = ' '.join(comment_text.split()).strip()

            if not author_name and not comment_text:
                return None

            if not author_name:
                author_name = "Unknown User"

            if len(comment_text) < 2:
                return None

            # Extract timestamp
            timestamp = ""
            time_elements = element.query_selector_all('a, span')
            for time_elem in time_elements:
                text = time_elem.text_content().strip()

                if len(text) > 50:
                    continue
                if text == author_name or text == comment_text:
                    continue

                if re.search(r'\d+\s*(m|h|d|j|w|hari|jam|menit|minggu|bulan|tahun|detik|s)', text, re.IGNORECASE) or \
                   re.search(r'just now|ago|yang lalu|baru saja', text, re.IGNORECASE):
                    timestamp = text
                    break

            # Extract likes count
            likes_count = 0
            try:
                like_elements = element.query_selector_all('[aria-label*="eaction"]')
                for like_elem in like_elements:
                    aria_label = like_elem.get_attribute('aria-label') or ""
                    match = re.search(r'(\d+)', aria_label)
                    if match:
                        likes_count = int(match.group(1))
                        break
            except Exception:
                pass

            # Extract replies count
            replies_count = 0
            try:
                reply_buttons = element.query_selector_all('text=/\\d+ repl|\\d+ balas/i')
                for reply_btn in reply_buttons:
                    text = reply_btn.text_content()
                    match = re.search(r'(\d+)', text)
                    if match:
                        replies_count = int(match.group(1))
                        break
            except Exception:
                pass

            comment_data = {
                **post_info,
                'comment_author_name': author_name,
                'comment_author_url': author_url,
                'comment_text': comment_text,
                'comment_timestamp': timestamp,
                'parent_comment_id': '',
                'likes_count': likes_count,
                'replies_count': replies_count,
                'crawled_at': datetime.now().isoformat()
            }

            return comment_data

        except Exception as e:
            logger.debug(f"Error parsing comment element: {e}")
            return None
