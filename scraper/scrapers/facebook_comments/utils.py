"""Utility functions for Facebook Comment Crawler"""

import random
import time
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from scraper.utils.logger import get_logger
from scraper.scrapers.facebook_comments.config import FBCommentConfig

logger = get_logger('scraper.facebook_comments.utils')


def random_delay(min_seconds: Optional[int] = None, max_seconds: Optional[int] = None) -> None:
    """Sleep for a random duration to simulate human behavior"""
    min_delay = min_seconds or FBCommentConfig.MIN_DELAY
    max_delay = max_seconds or FBCommentConfig.MAX_DELAY
    delay = random.uniform(min_delay, max_delay)
    logger.debug(f"Waiting {delay:.2f} seconds...")
    time.sleep(delay)


def human_like_scroll(page, scroll_amount: int = 300, pause_time: Optional[float] = None, selector: Optional[str] = None) -> None:
    """Perform human-like scrolling with automatic popup/dialog detection."""
    pause = pause_time or FBCommentConfig.SCROLL_PAUSE_TIME / 2

    increments = random.randint(3, 5)
    for i in range(increments):
        amount = scroll_amount // increments

        page.evaluate(f"""
            (info) => {{
                const amount = info.amount;
                const manualSelector = info.selector;

                function isScrollable(el) {{
                    if (!el) return false;
                    const style = window.getComputedStyle(el);
                    const overflowY = style.overflowY;
                    return (overflowY === 'auto' || overflowY === 'scroll') && (el.scrollHeight > el.clientHeight);
                }}

                function findScrollableChild(el) {{
                    if (isScrollable(el)) return el;
                    for (let child of el.children) {{
                        const found = findScrollableChild(child);
                        if (found) return found;
                    }}
                    return null;
                }}

                if (manualSelector) {{
                    const el = document.querySelector(manualSelector);
                    if (el) {{
                        const target = findScrollableChild(el) || el;
                        target.scrollBy(0, amount);
                        return;
                    }}
                }}

                const dialogs = Array.from(document.querySelectorAll('div[role="dialog"], div[tabindex="-1"]'))
                    .filter(el => {{
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetParent !== null;
                    }});

                if (dialogs.length > 0) {{
                    const topDialog = dialogs[dialogs.length - 1];
                    const scrollable = findScrollableChild(topDialog);
                    if (scrollable) {{
                        scrollable.scrollBy(0, amount);
                        return;
                    }}
                }}

                window.scrollBy(0, amount);
            }}
        """, {"amount": amount, "selector": selector})

        time.sleep(pause / increments + random.uniform(0, 0.1))


def save_cookies(cookies: list, identifier: str = "default") -> None:
    """Save browser cookies to file"""
    cookies_path = FBCommentConfig.get_cookies_path(identifier)
    try:
        with open(cookies_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        logger.info(f"Cookies saved to {cookies_path}")
    except Exception as e:
        logger.error(f"Failed to save cookies: {e}")


def load_cookies(identifier: str = "default") -> Optional[list]:
    """Load browser cookies from file"""
    cookies_path = FBCommentConfig.get_cookies_path(identifier)
    if not cookies_path.exists():
        logger.debug(f"No cookies file found at {cookies_path}")
        return None

    try:
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        logger.info(f"Cookies loaded from {cookies_path}")
        return cookies
    except Exception as e:
        logger.error(f"Failed to load cookies: {e}")
        return None


def parse_facebook_date(date_string: str) -> Optional[str]:
    """Parse Facebook date format to ISO format"""
    try:
        return date_string
    except Exception as e:
        logger.error(f"Failed to parse date '{date_string}': {e}")
        return None


def validate_url(url: str) -> bool:
    """Validate if URL is a Facebook URL"""
    valid_domains = ["facebook.com", "fb.com", "m.facebook.com", "web.facebook.com"]
    return any(domain in url.lower() for domain in valid_domains)


def extract_username_from_url(url: str) -> Optional[str]:
    """Extract username from Facebook profile URL"""
    try:
        url = url.rstrip('/')

        if "profile.php?id=" in url:
            return url.split("profile.php?id=")[-1].split("&")[0]
        else:
            parts = url.split("facebook.com/")
            if len(parts) > 1:
                username = parts[-1].split("/")[0].split("?")[0]
                return username
        return None
    except Exception as e:
        logger.error(f"Failed to extract username from URL '{url}': {e}")
        return None


def get_timestamp_string() -> str:
    """Get current timestamp as string for file naming"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def read_urls_from_file(filepath: str) -> List[str]:
    """Read URLs from a text file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        logger.info(f"Loaded {len(urls)} URLs from {filepath}")
        return urls
    except Exception as e:
        logger.error(f"Failed to read file {filepath}: {e}")
        return []
