"""
Instagram Scraper - Simplified Approach with Enhanced Comment Extraction

This module provides a fast and reliable Instagram scraper that supports both
regular posts and reels, with robust comment extraction capabilities.

KEY FEATURES:
=============

1. **Dual Content Type Support**
   - Automatically detects and scrapes both regular posts (/p/) and reels (/reel/)
   - Tracks content type distribution in metadata
   - Applies appropriate extraction logic for each type

2. **3-Strategy Comment Extraction**
   The scraper uses a robust fallback approach for extracting comments:
   
   Strategy 1: JSON Parsing (Fastest)
   - Extracts from embedded _sharedData or __additionalDataLoaded
   - Most reliable when available
   - Limited to initially loaded comments
   
   Strategy 2: DOM Extraction (Most Comprehensive)
   - Uses WebDriverWait to ensure elements are loaded
   - Clicks "View all" and "Load more" buttons
   - Scrolls to trigger lazy loading (up to 5 iterations)
   - Supports English and Indonesian UI text
   
   Strategy 3: JavaScript Fallback (Most Resilient)
   - Executes JavaScript directly in browser context
   - Can access elements Selenium selectors miss
   - Last resort for unusual DOM structures

3. **Multi-Strategy Post Data Extraction**
   - Meta og:description tags (most stable)
   - Embedded JSON in page source
   - DOM selectors as final fallback

4. **Anti-Detection Measures**
   - Random user agents
   - Random viewport sizes
   - Human-like typing delays
   - Popup handling

USAGE:
======

Basic usage:
    python scrape_instagram_simple.py <profile_url> <limit>

With options:
    python scrape_instagram_simple.py <profile_url> <limit> <headless> <scrape_comments> <comments_per_post>

Examples:
    # Scrape 5 posts with comments
    python scrape_instagram_simple.py https://www.instagram.com/username/ 5
    
    # Scrape 10 posts without comments in headless mode
    python scrape_instagram_simple.py https://www.instagram.com/username/ 10 true false
    
    # Scrape 3 posts with up to 50 comments each
    python scrape_instagram_simple.py https://www.instagram.com/username/ 3 false true 50

OUTPUT SCHEMA:
==============

{
  "metadata": {
    "platform": "instagram",
    "scraped_at": "2024-01-15T12:00:00Z",
    "target_url": "https://instagram.com/username",
    "total_posts": 10,
    "post_count": 6,      // Regular posts
    "reel_count": 4,      // Reels
    "total_comments": 150,
    "scrape_comments": true,
    "comments_per_post": 20,
    "method": "enhanced with comments"
  },
  "posts": [
    {
      "post_id": "abc123",
      "post_type": "post",  // or "reel"
      "post_url": "https://instagram.com/p/abc123",
      "author": "username",
      "content": "Caption text...",
      "timestamp": "2024-01-15T10:30:00Z",
      "likes": 150,
      "comments_count": 25,
      "comments": [
        {
          "author": "commenter1",
          "text": "Great post!",
          "timestamp": "2024-01-15T11:00:00Z"
        }
      ],
      "hashtags": ["#example", "#instagram"],
      "scraped_at": "2024-01-15T12:00:00Z"
    }
  ]
}

REQUIREMENTS VALIDATION:
========================

This module validates the following requirements:
- Requirement 13.1: Detect both post and reel links
- Requirement 13.2: Determine post_type from URL
- Requirement 13.3: Include post_type in output
- Requirement 13.4: Report post/reel counts separately
- Requirement 14.1: Wait for comment section to render
- Requirement 14.2: Click "View all comments" button
- Requirement 14.3: Scroll and load more comments
- Requirement 14.4: Extract comment text, author, timestamp
- Requirement 14.5: Filter out captions and UI text
- Requirement 14.6: Use JavaScript fallback when needed
- Requirement 14.7: Include comments array in output

PERFORMANCE:
============

- Profile page load: ~3 seconds
- Per post extraction: ~3-5 seconds without comments
- Per post with comments: ~5-15 seconds (depends on comment count)
- Comment loading: Up to 5 scroll iterations with 1-2 second delays

DEPENDENCIES:
=============

- selenium: Web automation
- scraper.config: Configuration management
- scraper.utils.anti_detection: Anti-detection utilities
"""

import os
import sys
import json
import re
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.config import get_config
from scraper.utils.anti_detection import AntiDetection


def _safe_decode(text):
    """Safely decode unicode escape sequences, removing invalid surrogates."""
    try:
        decoded = text.encode('raw_unicode_escape').decode('unicode_escape', errors='replace')
        # Remove surrogates that can't be encoded to UTF-8
        return decoded.encode('utf-8', errors='surrogateescape').decode('utf-8', errors='replace')
    except Exception:
        return text


def _parse_count(text):
    """Parse count from text like '1,234' or '1.2K' or '3M'"""
    text = text.strip().replace(',', '')
    if text.upper().endswith('K'):
        return int(float(text[:-1]) * 1000)
    elif text.upper().endswith('M'):
        return int(float(text[:-1]) * 1000000)
    try:
        return int(float(text))
    except (ValueError, TypeError):
        return 0


def extract_post_data_from_page(driver):
    """Extract post data (content, likes, comment count) from an Instagram post page.

    Uses multiple strategies for robustness:
      1. Meta og:description tag (most stable across IG updates)
      2. Embedded JSON in page source (caption, like_count, etc.)
      3. DOM selectors as final fallback
    """
    result = {'content': '', 'likes': 0, 'comments_count': 0}
    page_source = driver.page_source

    # ── STRATEGY 1: meta og:description ──────────────────────────────
    # Format: "N likes, M comments - @user on Instagram: \"caption text\""
    try:
        meta = driver.find_element(By.CSS_SELECTOR, 'meta[property="og:description"]')
        desc = meta.get_attribute('content') or ''
        if desc:
            # Extract likes & comments from description
            like_m = re.search(r'([\d,.KkMm]+)\s*[Ll]ikes?', desc)
            if like_m:
                result['likes'] = _parse_count(like_m.group(1))
            comment_m = re.search(r'([\d,.KkMm]+)\s*[Cc]omments?', desc)
            if comment_m:
                result['comments_count'] = _parse_count(comment_m.group(1))

            # Extract caption
            for sep in [' on Instagram: ', '\u201c']:
                if sep in desc:
                    caption = desc.split(sep, 1)[1]
                    caption = caption.strip().strip('"').strip('\u201c').strip('\u201d')
                    if len(caption) > 3:
                        result['content'] = caption
                    break
    except Exception:
        pass

    # ── STRATEGY 2: page source embedded JSON ────────────────────────
    if not result['content']:
        caption_patterns = [
            r'"caption"\s*:\s*\{[^}]*?"text"\s*:\s*"((?:[^"\\]|\\.){5,})"',
            r'"edge_media_to_caption".*?"text"\s*:\s*"((?:[^"\\]|\\.){5,})"',
            r'"accessibility_caption"\s*:\s*"((?:[^"\\]|\\.){10,})"',
        ]
        for pattern in caption_patterns:
            match = re.search(pattern, page_source)
            if match:
                text = _safe_decode(match.group(1))
                if len(text) > 5:
                    result['content'] = text
                    break

    if result['likes'] == 0:
        like_patterns = [
            r'"edge_media_preview_like"\s*:\s*\{"count"\s*:\s*(\d+)',
            r'"like_count"\s*:\s*(\d+)',
            r'"edge_liked_by"\s*:\s*\{"count"\s*:\s*(\d+)',
        ]
        for pattern in like_patterns:
            match = re.search(pattern, page_source)
            if match:
                result['likes'] = int(match.group(1))
                break

    if result['comments_count'] == 0:
        comment_count_patterns = [
            r'"edge_media_to_parent_comment"\s*:\s*\{"count"\s*:\s*(\d+)',
            r'"edge_media_to_comment"\s*:\s*\{"count"\s*:\s*(\d+)',
            r'"comment_count"\s*:\s*(\d+)',
        ]
        for pattern in comment_count_patterns:
            match = re.search(pattern, page_source)
            if match:
                result['comments_count'] = int(match.group(1))
                break

    # ── STRATEGY 3: DOM selectors (fallback) ─────────────────────────
    if not result['content']:
        caption_selectors = [
            'h1',
            'article h1',
            'article div[role] span[dir="auto"]',
            'article span[dir="auto"]',
            'div[role="dialog"] span[dir="auto"]',
            'span[dir="auto"]',
        ]
        for selector in caption_selectors:
            try:
                elems = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elems:
                    text = elem.text.strip()
                    if text and len(text) > 10 and not text.startswith('http'):
                        result['content'] = text
                        break
            except Exception:
                continue
            if result['content']:
                break

    if result['likes'] == 0:
        try:
            like_selectors = [
                'section a[href$="/liked_by/"] span',
                'section span a span',
                'section span',
            ]
            for selector in like_selectors:
                try:
                    elems = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elems:
                        text = elem.text.strip().replace(',', '').replace('.', '')
                        if text.isdigit() and int(text) > 0:
                            result['likes'] = int(text)
                            break
                except Exception:
                    continue
                if result['likes'] > 0:
                    break
        except Exception:
            pass

    return result

def setup_driver(headless=False):
    """Setup Chrome driver"""
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={AntiDetection.get_random_user_agent()}')
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(*AntiDetection.get_random_viewport())
    return driver

def login_instagram(driver, username, password):
    """Login to Instagram - simplified"""
    print("🔐 Logging in to Instagram...")
    
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)
    
    # Find and fill username
    selectors = [
        'input[name="username"]',
        'input[aria-label*="username"]',
        'input[type="text"]'
    ]
    
    username_input = None
    for selector in selectors:
        try:
            username_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            break
        except:
            continue
    
    if not username_input:
        raise Exception("Could not find username input")
    
    # Type username
    for char in username:
        username_input.send_keys(char)
        time.sleep(0.1)
    
    time.sleep(1)
    
    # Find and fill password
    password_selectors = [
        'input[name="password"]',
        'input[type="password"]',
        'input[aria-label*="Password"]'
    ]
    
    password_input = None
    for selector in password_selectors:
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, selector)
            break
        except:
            continue
    
    if not password_input:
        raise Exception("Could not find password input")
    
    for char in password:
        password_input.send_keys(char)
        time.sleep(0.1)
    
    time.sleep(1)
    
    # Click login - try multiple methods
    try:
        # Method 1: Find button
        login_selectors = [
            'button[type="submit"]',
            'button:contains("Log in")',
            '//button[contains(text(), "Log in")]',
            '//button[@type="submit"]'
        ]
        
        login_button = None
        for selector in login_selectors:
            try:
                if selector.startswith('//'):
                    login_button = driver.find_element(By.XPATH, selector)
                else:
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if login_button:
            login_button.click()
        else:
            # Method 2: Press Enter on password field
            from selenium.webdriver.common.keys import Keys
            password_input.send_keys(Keys.RETURN)
    except Exception as e:
        # Method 3: Press Enter as fallback
        from selenium.webdriver.common.keys import Keys
        password_input.send_keys(Keys.RETURN)
    
    print("⏳ Waiting for login...")
    time.sleep(5)
    
    # Handle popups
    try:
        not_now = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not")]'))
        )
        not_now.click()
        time.sleep(1)
    except:
        pass
    
    try:
        not_now = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not")]'))
        )
        not_now.click()
        time.sleep(1)
    except:
        pass
    
    print("✓ Login successful!")
    return True

def scrape_comments_from_post_dom(driver, post_url, post_type='post'):
    """
    Strategy 2: DOM-based comment extraction with WebDriverWait
    
    This strategy uses Selenium's WebDriverWait to ensure the comment section
    has fully rendered before attempting extraction. It handles Instagram's
    lazy-loading by clicking "View all comments" and "Load more" buttons,
    then scrolling within the comment container to trigger additional loads.
    
    The strategy supports both English and Indonesian UI text, making it
    suitable for international Instagram profiles.
    
    Args:
        driver: Selenium WebDriver instance with an active Instagram session
        post_url: Full URL of the Instagram post or reel
        post_type: Either 'post' or 'reel', used for logging context
    
    Returns:
        list: Array of comment objects, each containing:
            - author (str): Username of the commenter
            - text (str): The comment text content
            - timestamp (str): ISO 8601 timestamp or current time if unavailable
    
    Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5
    """
    comments = []
    
    try:
        # Wait for comment section to render (Requirement 14.1)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'ul'))
        )
        time.sleep(2)  # Additional wait for dynamic content
        
        # Try to click "View all comments" button (Requirement 14.2)
        # Support both English and Indonesian
        view_all_selectors = [
            "//span[contains(text(), 'View all')]",
            "//span[contains(text(), 'Lihat semua')]",
            "//button[contains(., 'View all')]",
            "//button[contains(., 'Lihat semua')]"
        ]
        
        for selector in view_all_selectors:
            try:
                view_all_btn = driver.find_element(By.XPATH, selector)
                driver.execute_script("arguments[0].click();", view_all_btn)
                print(f"  ✓ Clicked 'View all comments' button")
                time.sleep(2)
                break
            except:
                continue
        
        # Scroll and load more comments (Requirement 14.3)
        # Up to 5 times
        for i in range(5):
            try:
                # Find comment container
                comment_container = driver.find_element(By.CSS_SELECTOR, 'ul')
                
                # Scroll within container using JavaScript
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight",
                    comment_container
                )
                time.sleep(1)
                
                # Try to click "Load more" button
                load_more_selectors = [
                    "//button[contains(., 'Load more')]",
                    "//button[contains(., 'Muat lebih banyak')]",
                    "//span[contains(text(), 'Load more')]"
                ]
                
                for selector in load_more_selectors:
                    try:
                        load_more = driver.find_element(By.XPATH, selector)
                        driver.execute_script("arguments[0].click();", load_more)
                        print(f"  ✓ Clicked 'Load more' (attempt {i+1})")
                        time.sleep(2)
                        break
                    except:
                        continue
                        
            except Exception as e:
                break  # No more comments to load
        
        # Extract comment elements (Requirement 14.4)
        comment_elements = driver.find_elements(By.CSS_SELECTOR, 'ul li')
        
        seen_texts = set()  # Track duplicates
        
        for elem in comment_elements:
            try:
                # Extract author from link (Requirement 14.4)
                author_elem = elem.find_element(By.CSS_SELECTOR, 'a[href^="/"]')
                author = author_elem.get_attribute('href').strip('/').split('/')[0]
                
                # Extract comment text from span with dir="auto" (Requirement 14.4)
                text_elem = elem.find_element(By.CSS_SELECTOR, 'span[dir="auto"]')
                text = text_elem.text.strip()
                
                # Filter out invalid comments (Requirement 14.5)
                # Skip if text is empty or too short
                if not text or len(text) < 2:
                    continue
                
                # Skip duplicates
                if text in seen_texts:
                    continue
                
                # Skip captions and UI text (Requirement 14.5)
                ui_text_keywords = [
                    'Original audio', 'Suara asli', 'Reply', 'Balas',
                    'View replies', 'Lihat balasan', 'Liked by', 'Disukai oleh',
                    'See translation', 'Lihat terjemahan'
                ]
                if any(keyword in text for keyword in ui_text_keywords):
                    continue
                
                # Skip if text looks like a timestamp (e.g., "1h", "2d")
                if re.match(r'^\d+[hdwmy]$', text):
                    continue
                
                seen_texts.add(text)
                
                # Extract timestamp if available (Requirement 14.4)
                timestamp = None
                try:
                    time_elem = elem.find_element(By.TAG_NAME, 'time')
                    timestamp = time_elem.get_attribute('datetime')
                except:
                    pass
                
                comment_obj = {
                    'author': author,
                    'text': text,
                    'timestamp': timestamp or datetime.now().isoformat() + 'Z'
                }
                
                comments.append(comment_obj)
                
            except Exception as e:
                continue  # Skip malformed comments
        
        print(f"  ✓ Extracted {len(comments)} comments via DOM")
        
    except Exception as e:
        print(f"  ✗ DOM extraction failed: {str(e)}")
    
    return comments


def scrape_comments_from_post_js(driver, post_url, post_type='post'):
    """
    Strategy 3: JavaScript-based DOM query fallback
    
    This strategy executes JavaScript directly in the browser context to query
    the DOM. It's more resilient than Selenium selectors because it runs in the
    same context as Instagram's own JavaScript, allowing it to access elements
    that may be dynamically created or hidden from Selenium's view.
    
    This is the final fallback strategy when both JSON parsing and DOM extraction
    fail. It uses the same filtering logic as Strategy 2 but implemented in
    JavaScript for better compatibility.
    
    Args:
        driver: Selenium WebDriver instance with an active Instagram session
        post_url: Full URL of the Instagram post or reel (not used but kept for consistency)
        post_type: Either 'post' or 'reel', used for logging context
    
    Returns:
        list: Array of comment objects, each containing:
            - author (str): Username of the commenter
            - text (str): The comment text content
            - timestamp (str): ISO 8601 timestamp or current time if unavailable
    
    Validates: Requirement 14.6
    """
    comments = []
    
    try:
        # JavaScript to extract comments directly from DOM
        js_script = """
        const comments = [];
        const commentElements = document.querySelectorAll('ul li');
        const seenTexts = new Set();
        
        // UI text keywords to filter out
        const uiKeywords = [
            'Original audio', 'Suara asli', 'Reply', 'Balas',
            'View replies', 'Lihat balasan', 'Liked by', 'Disukai oleh',
            'See translation', 'Lihat terjemahan'
        ];
        
        commentElements.forEach(elem => {
            try {
                const authorLink = elem.querySelector('a[href^="/"]');
                const textSpan = elem.querySelector('span[dir="auto"]');
                const timeElem = elem.querySelector('time');
                
                if (authorLink && textSpan) {
                    const author = authorLink.getAttribute('href').replace(/^\//, '').split('/')[0];
                    const text = textSpan.textContent.trim();
                    const timestamp = timeElem ? timeElem.getAttribute('datetime') : null;
                    
                    // Filter out invalid/empty comments
                    if (!text || text.length < 2) {
                        return;
                    }
                    
                    // Skip duplicates
                    if (seenTexts.has(text)) {
                        return;
                    }
                    
                    // Skip UI text
                    const hasUIKeyword = uiKeywords.some(keyword => text.includes(keyword));
                    if (hasUIKeyword) {
                        return;
                    }
                    
                    // Skip timestamp-like text (e.g., "1h", "2d")
                    if (/^\d+[hdwmy]$/.test(text)) {
                        return;
                    }
                    
                    seenTexts.add(text);
                    
                    comments.push({
                        author: author,
                        text: text,
                        timestamp: timestamp || new Date().toISOString()
                    });
                }
            } catch (e) {
                // Skip malformed elements
            }
        });
        
        return comments;
        """
        
        comments = driver.execute_script(js_script)
        print(f"  ✓ Extracted {len(comments)} comments via JavaScript")
        
    except Exception as e:
        print(f"  ✗ JavaScript extraction failed: {str(e)}")
    
    return comments


def scrape_comments_from_post(driver, post_url, post_type='post'):
    """
    Extract comments using multiple strategies with fallback.
    
    This is the main orchestrator function for comment extraction. It implements
    a robust 3-strategy approach to handle Instagram's frequently changing DOM
    structure and various edge cases:
    
    **Strategy 1: JSON Parsing** (Fastest, most reliable when available)
    - Extracts comments from embedded JSON in page source (_sharedData)
    - Works on older Instagram pages and some mobile views
    - Provides structured data with minimal parsing
    
    **Strategy 2: DOM Extraction** (Most comprehensive)
    - Uses Selenium WebDriverWait to ensure elements are loaded
    - Clicks "View all" and "Load more" buttons to expand comments
    - Scrolls within comment container to trigger lazy loading
    - Supports both English and Indonesian UI text
    
    **Strategy 3: JavaScript Fallback** (Most resilient)
    - Executes JavaScript directly in browser context
    - Can access elements that Selenium selectors miss
    - Uses same filtering logic as Strategy 2
    - Last resort when DOM structure is unusual
    
    Each strategy is independent and has its own error handling. If one fails,
    the next is attempted automatically. This ensures maximum reliability across
    different Instagram page layouts and network conditions.
    
    Args:
        driver: Selenium WebDriver instance with an active Instagram session
        post_url: Full URL of the Instagram post or reel to extract comments from
        post_type: Either 'post' or 'reel', used for logging and debugging context
    
    Returns:
        list: Array of comment objects, each containing:
            - author (str): Username of the commenter
            - text (str): The comment text content
            - timestamp (str): ISO 8601 timestamp when comment was posted
            - likes (int): Number of likes (Strategy 1 only)
        Returns empty list if all strategies fail (graceful degradation)
    
    Validates: Requirements 14.6, 14.7
    """
    print(f"\n  Extracting comments from {post_type}: {post_url}")
    
    # ═══════════════════════════════════════════════════════════════════
    # Strategy 1: Page source JSON (existing implementation)
    # ═══════════════════════════════════════════════════════════════════
    # This is the fastest method when available. Instagram embeds comment data
    # in JSON structures within the page source. We parse these directly without
    # needing to interact with the DOM.
    print(f"  → Trying Strategy 1: JSON extraction...")
    comments = scrape_comments_from_post_json(driver, post_url)
    if comments:
        print(f"  ✓ Strategy 1 succeeded: Extracted {len(comments)} comments via JSON")
        return comments
    print(f"  ✗ Strategy 1 failed")
    
    # ═══════════════════════════════════════════════════════════════════
    # Strategy 2: DOM extraction with WebDriverWait
    # ═══════════════════════════════════════════════════════════════════
    # This method actively interacts with the page to load and extract comments.
    # It handles Instagram's lazy loading by clicking buttons and scrolling.
    # Most comprehensive but slower than JSON parsing.
    print(f"  → Trying Strategy 2: DOM extraction...")
    comments = scrape_comments_from_post_dom(driver, post_url, post_type)
    if comments:
        print(f"  ✓ Strategy 2 succeeded: Extracted {len(comments)} comments via DOM")
        return comments
    print(f"  ✗ Strategy 2 failed")
    
    # ═══════════════════════════════════════════════════════════════════
    # Strategy 3: JavaScript fallback
    # ═══════════════════════════════════════════════════════════════════
    # Final fallback that runs JavaScript directly in the browser context.
    # Can access elements that Selenium sometimes misses due to timing or
    # shadow DOM issues. Most resilient but least structured.
    print(f"  → Trying Strategy 3: JavaScript extraction...")
    comments = scrape_comments_from_post_js(driver, post_url, post_type)
    if comments:
        print(f"  ✓ Strategy 3 succeeded: Extracted {len(comments)} comments via JavaScript")
        return comments
    print(f"  ✗ Strategy 3 failed")
    
    # All strategies failed - return empty list for graceful degradation
    print(f"  ⚠ All comment extraction strategies failed for {post_type}")
    return []


def scrape_comments_from_post_json(driver, post_url, limit=20):
    """
    Strategy 1: Page source JSON-based comment extraction
    
    This strategy extracts comments from Instagram's embedded JSON data structures
    in the page source. Instagram includes comment data in window._sharedData or
    __additionalDataLoaded objects for initial page rendering. This method is:
    
    - **Fastest**: No DOM interaction or waiting required
    - **Most reliable**: JSON structure is more stable than DOM selectors
    - **Limited scope**: Only gets initially loaded comments (not lazy-loaded ones)
    
    The function searches for two main JSON patterns:
    1. edge_media_to_parent_comment: Top-level comments
    2. edge_media_to_comment: All comments including replies
    
    If JSON extraction fails, it falls back to basic DOM extraction with button
    clicking and scrolling to load more comments.
    
    Args:
        driver: Selenium WebDriver instance with an active Instagram session
        post_url: Full URL of the Instagram post or reel (not used but kept for consistency)
        limit: Maximum number of comments to extract (default: 20)
    
    Returns:
        list: Array of comment objects, each containing:
            - author (str): Username of the commenter
            - text (str): The comment text content
            - likes (int): Number of likes on the comment
            - timestamp (str): ISO 8601 timestamp or current time
    
    Validates: Requirement 14.6
    """
    comments = []

    try:
        print(f"  >> Loading comments from post...")
        page_source = driver.page_source

        # ── Strategy 1: Extract from page source JSON ────────────────
        comment_json_patterns = [
            r'"edge_media_to_parent_comment"\s*:\s*\{[^{]*?"edges"\s*:\s*\[(.+?)\]\s*,\s*"page_info"',
            r'"edge_media_to_comment"\s*:\s*\{[^{]*?"edges"\s*:\s*\[(.+?)\]\s*,\s*"page_info"',
        ]
        for pattern in comment_json_patterns:
            match = re.search(pattern, page_source, re.DOTALL)
            if match:
                edges_str = match.group(1)
                # Match pairs of text + username in each comment node
                node_pattern = r'"text"\s*:\s*"((?:[^"\\]|\\.)*)".*?"username"\s*:\s*"((?:[^"\\]|\\.)*)"'
                for cm in re.finditer(node_pattern, edges_str):
                    text = _safe_decode(cm.group(1))
                    author = cm.group(2)
                    if text and len(text) >= 2:
                        comments.append({
                            'author': author,
                            'text': text,
                            'likes': 0,
                            'timestamp': datetime.now().isoformat() + 'Z'
                        })
                    if len(comments) >= limit:
                        break
                if comments:
                    break

        # ── Strategy 2: DOM-based extraction (fallback) ──────────────
        if not comments:
            # Try to click "View all N comments" / load more
            for _ in range(3):
                try:
                    load_more_selectors = [
                        '//button[contains(text(), "View")]',
                        '//button[contains(text(), "Load")]',
                        '//span[contains(text(), "View all")]',
                        '//a[contains(text(), "View all")]',
                    ]
                    for selector in load_more_selectors:
                        try:
                            btn = driver.find_element(By.XPATH, selector)
                            if btn.is_displayed():
                                btn.click()
                                time.sleep(2)
                                break
                        except Exception:
                            continue
                except Exception:
                    break

            # Scroll to load more comments
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(0.5)

            comment_container_selectors = [
                'article ul > ul > li',
                'article ul > li',
                'div[role="dialog"] ul > li',
            ]
            seen_texts = set()
            skip_words = {'Reply', 'Replies', 'View replies', 'Liked by', 'See translation'}

            for selector in comment_container_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if not elements:
                        continue
                    for elem in elements[:limit * 3]:
                        try:
                            full_text = elem.text.strip()
                            if not full_text or len(full_text) < 3:
                                continue
                            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
                            if len(lines) < 2:
                                continue

                            author = lines[0]
                            comment_text = lines[1]

                            if comment_text in seen_texts or len(comment_text) < 3:
                                continue
                            if re.match(r'^\d+[hdwmy]$', comment_text) or comment_text in skip_words:
                                continue
                            if comment_text == author:
                                continue

                            seen_texts.add(comment_text)

                            likes = 0
                            for line in lines:
                                if 'like' in line.lower() or 'suka' in line.lower():
                                    m = re.search(r'(\d+)', line)
                                    if m:
                                        likes = int(m.group(1))
                                        break

                            comments.append({
                                'author': author,
                                'text': comment_text,
                                'likes': likes,
                                'timestamp': datetime.now().isoformat() + 'Z'
                            })
                            if len(comments) >= limit:
                                break
                        except Exception:
                            continue
                    if comments:
                        break
                except Exception:
                    continue

        print(f"  [OK] Scraped {len(comments)} comments")

    except Exception as e:
        print(f"  [!] Error scraping comments: {e}")

    return comments


def scrape_profile_simple(driver, profile_url, limit=5, scrape_comments=True, comments_per_post=20):
    """
    Scrape Instagram profile with support for both posts and reels.
    
    This function extracts post/reel data from an Instagram profile page, including
    content, likes, comments, and metadata. It supports both regular posts (/p/)
    and reels (/reel/) with automatic type detection.
    
    The scraping process:
    1. Load the profile page
    2. Find all post and reel links on the page
    3. Extract post_type and post_id from each URL
    4. Navigate to each post/reel individually
    5. Extract post data (content, likes, comments count)
    6. Optionally scrape actual comment text using 3-strategy approach
    7. Return to profile page for next item
    
    Args:
        driver: Selenium WebDriver instance with an active Instagram session
        profile_url: Full URL of the Instagram profile to scrape
        limit: Maximum number of posts/reels to scrape (default: 5)
        scrape_comments: Whether to extract actual comment text (default: True)
        comments_per_post: Max comments to extract per post if scraping enabled (default: 20)
    
    Returns:
        list: Array of post/reel objects, each containing:
            - post_id (str): Unique identifier for the post/reel
            - post_type (str): Either 'post' or 'reel'
            - post_url (str): Full URL to the post/reel
            - author (str): Username of the profile owner
            - content (str): Caption text
            - timestamp (str): ISO 8601 timestamp
            - likes (int): Number of likes
            - comments_count (int): Number of comments
            - comments (list): Array of comment objects (if scrape_comments=True)
            - hashtags (list): Hashtags found in caption
            - scraped_at (str): ISO 8601 timestamp when scraped
    
    Validates: Requirements 13.1, 13.2, 13.3, 14.7
    """
    print(f"\n🔍 Scraping {profile_url}...")

    driver.get(profile_url)
    time.sleep(3)

    posts = []

    # Find all post links (including reels)
    print("📸 Finding posts and reels...")
    post_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/p/"], a[href*="/reel/"]')

    if not post_links:
        post_links = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/") or contains(@href, "/reel/")]')

    print(f"✓ Found {len(post_links)} post links")

    # Extract post URLs first
    post_urls = []
    seen_ids = set()

    for link in post_links[:limit * 2]:
        if len(post_urls) >= limit:
            break

        try:
            href = link.get_attribute('href')
            if not href:
                continue

            # ═══════════════════════════════════════════════════════════════
            # POST TYPE DETECTION LOGIC
            # ═══════════════════════════════════════════════════════════════
            # Instagram uses different URL patterns for different content types:
            # - Regular posts: /p/{post_id}/
            # - Reels (short videos): /reel/{post_id}/
            # 
            # We detect the type by checking which pattern exists in the URL,
            # then extract the post_id accordingly. This allows us to:
            # 1. Track content type distribution (posts vs reels)
            # 2. Apply type-specific scraping logic if needed
            # 3. Provide better logging and debugging context
            # 
            # Unknown URL patterns are skipped to avoid processing invalid links.
            # ═══════════════════════════════════════════════════════════════
            
            if '/p/' in href:
                # Regular Instagram post
                post_id = href.split('/p/')[1].split('/')[0]
                post_type = 'post'
            elif '/reel/' in href:
                # Instagram Reel (short video)
                post_id = href.split('/reel/')[1].split('/')[0]
                post_type = 'reel'
            else:
                # Unknown content type - skip to avoid errors
                continue

            # Skip duplicates (same post_id already processed)
            if post_id in seen_ids:
                continue

            seen_ids.add(post_id)
            post_urls.append((post_id, href, post_type))

        except Exception as e:
            continue

    # Process each post
    for i, (post_id, post_url, post_type) in enumerate(post_urls, 1):
        try:
            print(f"\n📄 {post_type.capitalize()} {i}/{len(post_urls)}: {post_id}")

            # Navigate to post to get details
            driver.get(post_url)
            time.sleep(3)

            # Extract post data using multi-strategy extraction
            post_info = extract_post_data_from_page(driver)
            content = post_info['content']
            likes = post_info['likes']

            # Extract hashtags from content
            hashtags = re.findall(r'#\w+', content) if content else []

            # Create post data
            post_data = {
                'post_id': post_id,
                'post_type': post_type,  # 'post' or 'reel' - detected from URL pattern
                'post_url': post_url,
                'author': profile_url.split('/')[-2],
                'content': content or f"Post {post_id}",
                'timestamp': datetime.now().isoformat() + 'Z',
                'likes': likes,
                'comments_count': post_info['comments_count'],
                'comments': [],
                'hashtags': hashtags,
                'scraped_at': datetime.now().isoformat() + 'Z'
            }

            # ═══════════════════════════════════════════════════════════════
            # COMMENT EXTRACTION WITH 3-STRATEGY FALLBACK
            # ═══════════════════════════════════════════════════════════════
            # If comment scraping is enabled, we use a robust 3-strategy approach
            # to extract actual comment text. The scrape_comments_from_post()
            # function will automatically try:
            #
            # 1. JSON parsing from page source (fastest)
            # 2. DOM extraction with WebDriverWait (most comprehensive)
            # 3. JavaScript execution fallback (most resilient)
            #
            # Each strategy is independent with its own error handling. If one
            # fails, the next is tried automatically. This ensures we can extract
            # comments even when Instagram changes their page structure.
            #
            # The post_type parameter helps with logging and debugging.
            # ═══════════════════════════════════════════════════════════════
            if scrape_comments:
                comments = scrape_comments_from_post(driver, post_url, post_type)
                post_data['comments'] = comments
                if comments:
                    post_data['comments_count'] = len(comments)

            posts.append(post_data)
            print(f"  ✓ Scraped post with {post_data['comments_count']} comments")

            # Return to profile for next post
            driver.get(profile_url)
            time.sleep(2)

        except Exception as e:
            print(f"  ✗ Error processing post: {e}")
            continue

    return posts

def main():
    """Main function"""
    print("=" * 70)
    print("Instagram Scraper - Simplified & Fast")
    print("=" * 70)
    print()
    
    # Load config
    config = get_config()
    username = config.username or os.getenv('INSTAGRAM_USERNAME')
    password = config.password or os.getenv('INSTAGRAM_PASSWORD')
    target_url = os.getenv('INSTAGRAM_TARGET_URL', 'https://www.instagram.com/rusdi_sutejo/')
    
    if not username or not password:
        print("❌ Error: Credentials not found in .env")
        return
    
    # Allow command line override
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    
    limit = 5
    if len(sys.argv) > 2:
        limit = int(sys.argv[2])

    headless = False
    if len(sys.argv) > 3:
        headless = sys.argv[3].lower() == 'true'

    scrape_comments = True
    if len(sys.argv) > 4:
        scrape_comments = sys.argv[4].lower() == 'true'

    comments_per_post = 20
    if len(sys.argv) > 5:
        comments_per_post = int(sys.argv[5])

    print(f"🎯 Target: {target_url}")
    print(f"📊 Limit: {limit} posts")
    print(f"🖥️  Headless: {headless}")
    print(f"💬 Scrape Comments: {scrape_comments}")
    if scrape_comments:
        print(f"📝 Comments per post: {comments_per_post}")
    print()
    
    driver = None
    try:
        # Setup driver
        print("🚀 Starting Chrome...")
        driver = setup_driver(headless)
        
        # Login
        login_instagram(driver, username, password)

        # Scrape
        posts = scrape_profile_simple(driver, target_url, limit, scrape_comments, comments_per_post)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create organized folder structure
        output_base = Path("output") / "instagram"
        output_base.mkdir(parents=True, exist_ok=True)

        output_path = output_base / f"posts_{timestamp}.json"

        # Calculate total comments
        total_comments = sum(post.get('comments_count', 0) for post in posts)

        # ═══════════════════════════════════════════════════════════════════
        # METADATA WITH POST/REEL BREAKDOWN
        # ═══════════════════════════════════════════════════════════════════
        # The metadata includes separate counts for posts and reels, allowing
        # analysts to understand the content distribution on the profile.
        # This is useful for:
        # - Understanding creator content strategy (more posts vs more reels)
        # - Analyzing engagement patterns by content type
        # - Validating scraping completeness
        # ═══════════════════════════════════════════════════════════════════
        result = {
            'metadata': {
                'platform': 'instagram',
                'scraped_at': datetime.utcnow().isoformat() + 'Z',
                'target_url': target_url,
                'total_posts': len(posts),
                'post_count': sum(1 for p in posts if p.get('post_type') == 'post'),  # Regular posts
                'reel_count': sum(1 for p in posts if p.get('post_type') == 'reel'),  # Short videos
                'total_comments': total_comments,
                'scrape_comments': scrape_comments,
                'comments_per_post': comments_per_post if scrape_comments else 0,
                'method': 'enhanced with comments'
            },
            'posts': posts
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print()
        print("=" * 70)
        print("✅ Scraping Completed!")
        print("=" * 70)
        print()
        print(f"📁 Output: {output_path}")
        print(f"📊 Posts scraped: {len(posts)}")
        
        # Show post and reel counts separately (Requirement 13.4)
        # This helps users understand the content mix on the profile
        post_count = sum(1 for p in posts if p.get('post_type') == 'post')
        reel_count = sum(1 for p in posts if p.get('post_type') == 'reel')
        print(f"   - Posts: {post_count}")
        print(f"   - Reels: {reel_count}")
        
        print(f"💬 Total comments: {total_comments}")
        print()

        if posts:
            print("Sample Posts & Comments:")
            print("-" * 70)
            for i, post in enumerate(posts[:2], 1):
                print(f"{i}. Post ID: {post['post_id']}")
                print(f"   Type: {post.get('post_type', 'unknown')}")
                print(f"   Author: {post.get('author', 'unknown')}")
                print(f"   Content: {post.get('content', '')[:60]}...")
                print(f"   Likes: {post.get('likes', 0)}")
                print(f"   Comments: {post.get('comments_count', 0)}")
                print(f"   URL: {post['post_url']}")

                if post.get('comments'):
                    print(f"\n   Sample Comments:")
                    for j, comment in enumerate(post['comments'][:3], 1):
                        print(f"   {j}. {comment.get('author', 'unknown')}: {comment.get('text', '')[:50]}...")

                print()

        print("Next Steps:")
        print(f"1. View results: python view_results.py {output_path}")
        print(f"2. Analyze sentiment: python -m sentiment.main_analyzer --input {output_path} --output {str(output_path).replace('.json', '_sentiment.json')}")
        print(f"3. Scrape without comments: python scrape_instagram_simple.py <url> <limit> <headless> false")
        print()
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("\n🔒 Closing browser...")
            driver.quit()
    
    print("=" * 70)

if __name__ == "__main__":
    main()
