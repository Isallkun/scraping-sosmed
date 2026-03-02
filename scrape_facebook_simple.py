"""
Facebook Scraper - Simplified Approach

Simple and reliable Facebook scraper following the same pattern as Instagram scraper.

USAGE:
    python scrape_facebook_simple.py <profile_url> <limit> [headless]

EXAMPLES:
    python scrape_facebook_simple.py https://www.facebook.com/username 10
    python scrape_facebook_simple.py https://www.facebook.com/username 5 true
"""

import os
import sys
import json
import time
import re
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.utils.anti_detection import AntiDetection


def setup_driver(headless=False):
    """Setup Chrome driver with anti-detection"""
    options = Options()
    if headless:
        options.add_argument('--headless=new')
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f'user-agent={AntiDetection.get_random_user_agent()}')
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(*AntiDetection.get_random_viewport())
    
    # Remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver


def login_facebook(driver, username, password):
    """Login to Facebook"""
    print(f"\n🔐 Logging in to Facebook...")
    print(f"   Username: {username}")
    
    try:
        driver.get("https://www.facebook.com/login")
        time.sleep(3)
        
        # Enter email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]'))
        )
        email_input.clear()
        for char in username:
            email_input.send_keys(char)
            time.sleep(0.05)
        
        time.sleep(1)
        
        # Enter password
        password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="pass"]')
        password_input.clear()
        for char in password:
            password_input.send_keys(char)
            time.sleep(0.05)
        
        time.sleep(1)
        
        # Click login
        login_button = driver.find_element(By.CSS_SELECTOR, 'button[name="login"]')
        login_button.click()
        
        print("   ⏳ Waiting for login...")
        time.sleep(5)
        
        current_url = driver.current_url
        
        # Check for 2FA
        if 'two_step_verification' in current_url or 'checkpoint' in current_url:
            print("   ⚠️  Two-Factor Authentication detected!")
            print("   📱 Please complete 2FA in the browser window...")
            print("   ⏳ Waiting 60 seconds for you to complete 2FA...")
            
            for i in range(60):
                time.sleep(1)
                current_url = driver.current_url
                if 'two_step_verification' not in current_url and 'checkpoint' not in current_url and 'login' not in current_url:
                    print(f"   ✅ 2FA completed!")
                    break
                if i % 10 == 0 and i > 0:
                    print(f"   ⏳ Still waiting... ({60-i}s remaining)")
            
            current_url = driver.current_url
        
        # Check if login successful
        if 'login' in current_url.lower():
            print("   ❌ Login failed - still on login page")
            return False
        
        print(f"   ✅ Login successful!")
        print(f"   📍 Current URL: {current_url}")
        return True
        
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False


def scroll_to_load_posts(driver, scroll_count=3):
    """Scroll page to load more posts"""
    for i in range(scroll_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        print(f"   📜 Scrolled {i+1}/{scroll_count}")
        
        # Check how many links we have so far
        link_count = driver.execute_script("""
            const links = document.querySelectorAll('a[href*="/posts/"], a[href*="/videos/"], a[href*="/reel/"]');
            return links.length;
        """)
        print(f"      Found {link_count} post links so far...")


def extract_posts_from_page(driver, limit=10):
    """Extract posts from Facebook page"""
    posts = []
    seen_urls = set()
    
    print(f"\n📝 Extracting posts...")
    
    # Scroll to load posts - increase scroll count
    scroll_to_load_posts(driver, scroll_count=8)
    
    # Find all post links using JavaScript (more reliable than CSS selectors)
    try:
        post_links_js = driver.execute_script("""
            const links = [];
            const seen = new Set();
            
            // Find all anchor tags
            const allLinks = document.querySelectorAll('a[href]');
            
            for (const link of allLinks) {
                const href = link.getAttribute('href');
                if (!href) continue;
                
                // Check if it's a post, video, or reel URL
                if (href.includes('/posts/') || href.includes('/videos/') || href.includes('/reel/')) {
                    // Clean URL
                    const cleanUrl = href.split('?')[0];
                    
                    // Extract ID
                    let postId = '';
                    if (cleanUrl.includes('/posts/')) {
                        const parts = cleanUrl.split('/posts/');
                        if (parts.length > 1) {
                            postId = parts[1].split('/')[0];
                        }
                    } else if (cleanUrl.includes('/videos/')) {
                        const parts = cleanUrl.split('/videos/');
                        if (parts.length > 1) {
                            postId = parts[1].split('/')[0];
                        }
                    } else if (cleanUrl.includes('/reel/')) {
                        const parts = cleanUrl.split('/reel/');
                        if (parts.length > 1) {
                            postId = parts[1].split('/')[0];
                        }
                    }
                    
                    // Validate: ID should be long enough
                    if (postId && postId.length > 5 && !seen.has(postId)) {
                        seen.add(postId);
                        
                        // Make absolute URL
                        let fullUrl = cleanUrl;
                        if (cleanUrl.startsWith('/')) {
                            fullUrl = 'https://www.facebook.com' + cleanUrl;
                        }
                        
                        links.push(fullUrl);
                    }
                }
            }
            
            return links;
        """)
        
        print(f"   ✓ Found {len(post_links_js)} potential post links via JavaScript")
        
        # Limit to requested number
        post_links = post_links_js[:limit]
        
    except Exception as e:
        print(f"   ⚠️  Error finding post links with JS: {e}")
        post_links = []
    
    # Fallback: try CSS selectors if JS didn't work
    if not post_links:
        print(f"   ⚠️  JavaScript didn't find links, trying CSS selectors...")
        try:
            all_links = driver.find_elements(By.CSS_SELECTOR, 'a[href]')
            print(f"      Total <a> tags found: {len(all_links)}")
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if not href:
                        continue
                    
                    # Check for post/video/reel URLs
                    if '/posts/' in href or '/videos/' in href or '/reel/' in href:
                        clean_url = href.split('?')[0]
                        
                        # Extract ID for validation
                        if '/posts/' in clean_url:
                            post_id = clean_url.split('/posts/')[1].split('/')[0]
                        elif '/videos/' in clean_url:
                            post_id = clean_url.split('/videos/')[1].split('/')[0]
                        else:
                            post_id = clean_url.split('/reel/')[1].split('/')[0]
                        
                        if post_id and len(post_id) > 5 and post_id not in seen_urls:
                            seen_urls.add(post_id)
                            post_links.append(clean_url)
                            
                            if len(post_links) >= limit:
                                break
                except:
                    continue
                    
            print(f"   ✓ Found {len(post_links)} post links via CSS")
        except Exception as e:
            print(f"   ⚠️  CSS selector fallback also failed: {e}")
    
    # Debug: print page source snippet if no links found
    if not post_links:
        print(f"\n   🔍 DEBUG: Checking page content...")
        page_text = driver.execute_script("return document.body.innerText;")
        print(f"      Page text length: {len(page_text)} chars")
        print(f"      Page text preview: {page_text[:200]}...")
        
        # Check if we're actually on the profile page
        current_url = driver.current_url
        print(f"      Current URL: {current_url}")
        
        # Try to find any post-like elements
        article_count = len(driver.find_elements(By.CSS_SELECTOR, '[role="article"]'))
        print(f"      Articles found: {article_count}")
    
    if not post_links:
        print(f"   ❌ No post links found. The profile might be private or have no posts.")
        return []
    
    print(f"   ✅ Found {len(post_links)} valid posts to scrape")
    
    # Extract data from each post
    for idx, post_url in enumerate(post_links, 1):
        print(f"\n   📄 Post {idx}/{len(post_links)}")
        print(f"      URL: {post_url[:80]}...")
        
        try:
            # Navigate to post
            driver.get(post_url)
            time.sleep(4)  # Wait for page to load
            
            # Extract post data
            post_data = extract_post_data(driver, post_url)
            
            if post_data and post_data.get('content'):  # Only add if has content
                posts.append(post_data)
                print(f"      ✅ Type: {post_data['post_type']}")
                print(f"      ✅ Caption: {post_data['content'][:60]}...")
                print(f"      ✅ Comments: {len(post_data.get('comments', []))}")
            else:
                print(f"      ⚠️  No content extracted, skipping")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
            continue
    
    return posts


def extract_post_data(driver, post_url):
    """Extract data from a single Facebook post with comments"""
    
    # Determine post type from URL
    if '/videos/' in post_url:
        post_type = 'video'
    elif '/reel/' in post_url:
        post_type = 'reel'
    else:
        post_type = 'post'
    
    post_data = {
        'post_id': '',
        'post_type': post_type,
        'platform': 'facebook',
        'post_url': post_url,
        'author': '',
        'content': '',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'likes': 0,
        'comments_count': 0,
        'shares': 0,
        'media_type': 'text',
        'hashtags': [],
        'comments': [],
        'scraped_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Extract post ID from URL
    try:
        if '/posts/' in post_url:
            post_data['post_id'] = post_url.split('/posts/')[1].split('/')[0].split('?')[0]
        elif '/videos/' in post_url:
            post_data['post_id'] = post_url.split('/videos/')[1].split('/')[0].split('?')[0]
        elif '/reel/' in post_url:
            post_data['post_id'] = post_url.split('/reel/')[1].split('/')[0].split('?')[0]
        else:
            post_data['post_id'] = f"fb_{int(time.time() * 1000)}"
    except:
        post_data['post_id'] = f"fb_{int(time.time() * 1000)}"
    
    try:
        # Wait for page to load
        time.sleep(2)
        
        # Extract author - try multiple selectors
        try:
            author_selectors = [
                'h2 a strong',
                'h2 strong a',
                'h3 a strong',
                'span strong a',
                'a[role="link"] strong'
            ]
            for selector in author_selectors:
                try:
                    author_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    author = author_elem.text.strip()
                    if author and len(author) > 0 and not author.isdigit():
                        post_data['author'] = author
                        break
                except:
                    continue
        except:
            pass
        
        # Extract content/caption using multiple strategies
        content_found = False
        
        # Strategy 1: Look for the main post content div
        try:
            # Facebook often uses div with specific data attributes for post content
            content_selectors = [
                'div[data-ad-comet-preview="message"]',
                'div[data-ad-preview="message"]',
                '[role="article"] div[dir="auto"]',
                'div[dir="auto"][style*="text-align"]'
            ]
            
            max_length = 0
            best_content = ''
            
            for selector in content_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        # Filter out short texts, navigation items, etc.
                        if text and len(text) > 20 and len(text) > max_length:
                            # Avoid UI elements
                            if not any(x in text.lower() for x in ['like', 'comment', 'share', 'see more', 'lihat selengkapnya']):
                                max_length = len(text)
                                best_content = text
                                content_found = True
                except:
                    continue
            
            if best_content:
                post_data['content'] = best_content
        except:
            pass
        
        # Strategy 2: Use JavaScript to find content
        if not content_found:
            try:
                js_content = driver.execute_script("""
                    // Find the article/post container
                    const article = document.querySelector('[role="article"]');
                    if (!article) return null;
                    
                    // Find all div elements with dir="auto" (Facebook's content divs)
                    const divs = article.querySelectorAll('div[dir="auto"]');
                    
                    let longestText = '';
                    for (const div of divs) {
                        const text = div.textContent.trim();
                        // Must be longer than 20 chars and not contain UI keywords
                        if (text.length > 20 && text.length > longestText.length) {
                            const lower = text.toLowerCase();
                            if (!lower.includes('like') && 
                                !lower.includes('comment') && 
                                !lower.includes('share') &&
                                !lower.includes('see more')) {
                                longestText = text;
                            }
                        }
                    }
                    
                    return longestText || null;
                """)
                
                if js_content and len(js_content) > 20:
                    post_data['content'] = js_content
                    content_found = True
            except:
                pass
        
        # Extract hashtags from content
        if post_data['content']:
            hashtags = re.findall(r'#(\w+)', post_data['content'])
            post_data['hashtags'] = hashtags
        
        # Determine media type
        try:
            if driver.find_elements(By.CSS_SELECTOR, 'video'):
                post_data['media_type'] = 'video'
            elif driver.find_elements(By.CSS_SELECTOR, 'img[src*="scontent"]'):
                post_data['media_type'] = 'image'
        except:
            pass
        
        # Extract engagement metrics from page source (more reliable than DOM)
        page_source = driver.page_source
        
        # Extract likes
        try:
            like_patterns = [
                r'(\d+)\s+[Ll]ikes?',
                r'(\d+)\s+reactions?',
                r'(\d+)\s+[Ss]uka'
            ]
            for pattern in like_patterns:
                match = re.search(pattern, page_source)
                if match:
                    post_data['likes'] = int(match.group(1))
                    break
        except:
            pass
        
        # Extract comment count
        try:
            comment_patterns = [
                r'(\d+)\s+[Cc]omments?',
                r'(\d+)\s+[Kk]omentar'
            ]
            for pattern in comment_patterns:
                match = re.search(pattern, page_source)
                if match:
                    post_data['comments_count'] = int(match.group(1))
                    break
        except:
            pass
        
        # Extract share count
        try:
            share_patterns = [
                r'(\d+)\s+[Ss]hares?',
                r'(\d+)\s+[Bb]agikan',
                r'(\d+)\s+kali dibagikan'
            ]
            for pattern in share_patterns:
                match = re.search(pattern, page_source)
                if match:
                    post_data['shares'] = int(match.group(1))
                    break
        except:
            pass
        
        # Extract comments
        try:
            comments = extract_comments(driver, post_data['comments_count'])
            post_data['comments'] = comments
            if comments:
                print(f"      💬 Extracted {len(comments)} comments")
        except Exception as e:
            print(f"      ⚠️  Comment extraction failed: {e}")
        
    except Exception as e:
        print(f"      ⚠️  Error extracting post data: {e}")
    
    return post_data


def extract_comments(driver, expected_count=0):
    """Extract comments from Facebook post"""
    comments = []
    
    try:
        # Scroll down to load comments section
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(2)
        
        # Try to click "View more comments" buttons
        try:
            view_more_buttons = driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'View more comments') or contains(text(), 'Lihat komentar lainnya')]")
            for button in view_more_buttons[:3]:  # Click up to 3 times
                try:
                    button.click()
                    time.sleep(1)
                except:
                    pass
        except:
            pass
        
        # Find comment elements
        # Facebook comments are usually in divs with specific structure
        comment_selectors = [
            '[role="article"] div[dir="auto"]',
            'div[data-ad-comet-preview="message"]',
            'div[data-ad-preview="message"]'
        ]
        
        seen_texts = set()
        
        for selector in comment_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for elem in elements:
                    try:
                        text = elem.text.strip()
                        
                        # Filter: must be reasonable length, not duplicate
                        if not text or len(text) < 3 or len(text) > 1000:
                            continue
                        
                        if text in seen_texts:
                            continue
                        
                        # Filter out UI elements and the main post content
                        if any(x in text.lower() for x in ['like', 'reply', 'share', 'just now', 'minutes ago', 'hours ago']):
                            continue
                        
                        # Try to find author (usually in a link before the comment)
                        author = 'Unknown'
                        try:
                            parent = elem.find_element(By.XPATH, '..')
                            author_link = parent.find_element(By.CSS_SELECTOR, 'a[role="link"]')
                            author = author_link.text.strip()
                        except:
                            pass
                        
                        comment_data = {
                            'author': author,
                            'text': text,
                            'timestamp': datetime.utcnow().isoformat() + 'Z',
                            'likes': 0
                        }
                        
                        comments.append(comment_data)
                        seen_texts.add(text)
                        
                        # Stop if we have enough comments
                        if expected_count > 0 and len(comments) >= expected_count:
                            break
                            
                    except:
                        continue
                        
                if expected_count > 0 and len(comments) >= expected_count:
                    break
                    
            except:
                continue
        
        # Remove duplicates and limit
        unique_comments = []
        seen = set()
        for c in comments:
            if c['text'] not in seen:
                seen.add(c['text'])
                unique_comments.append(c)
        
        return unique_comments[:50]  # Limit to 50 comments
        
    except Exception as e:
        print(f"      ⚠️  Error extracting comments: {e}")
        return []


def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python scrape_facebook_simple.py <profile_url> <limit> [headless]")
        print("\nExamples:")
        print("  python scrape_facebook_simple.py https://www.facebook.com/username 10")
        print("  python scrape_facebook_simple.py https://www.facebook.com/username 5 true")
        sys.exit(1)
    
    profile_url = sys.argv[1]
    limit = int(sys.argv[2])
    headless = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    
    print("=" * 70)
    print("Facebook Scraper - Simplified")
    print("=" * 70)
    print(f"Profile URL: {profile_url}")
    print(f"Post limit: {limit}")
    print(f"Headless: {headless}")
    print("=" * 70)
    
    # Get credentials from environment
    from dotenv import load_dotenv
    load_dotenv()
    
    username = os.getenv('FACEBOOK_USERNAME')
    password = os.getenv('FACEBOOK_PASSWORD')
    
    if not username or not password:
        print("\n❌ Error: Facebook credentials not found in .env file")
        print("   Please set FACEBOOK_USERNAME and FACEBOOK_PASSWORD")
        sys.exit(1)
    
    # Setup driver
    driver = setup_driver(headless=headless)
    
    try:
        # Login
        if not login_facebook(driver, username, password):
            print("\n❌ Login failed. Exiting...")
            return
        
        # Navigate to profile
        print(f"\n📱 Navigating to profile: {profile_url}")
        driver.get(profile_url)
        time.sleep(5)
        
        # Extract posts
        posts = extract_posts_from_page(driver, limit=limit)
        
        # Calculate statistics
        post_count = sum(1 for p in posts if p.get('post_type') == 'post')
        video_count = sum(1 for p in posts if p.get('post_type') == 'video')
        reel_count = sum(1 for p in posts if p.get('post_type') == 'reel')
        total_comments = sum(len(p.get('comments', [])) for p in posts)
        
        # Create output
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path('output/facebook/raw')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f'posts_{timestamp}.json'
        
        result = {
            'metadata': {
                'platform': 'facebook',
                'scraped_at': datetime.utcnow().isoformat() + 'Z',
                'target_url': profile_url,
                'total_posts': len(posts),
                'post_count': post_count,
                'video_count': video_count,
                'reel_count': reel_count,
                'total_comments': total_comments,
                'method': 'simple_scraper_enhanced'
            },
            'posts': posts
        }
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n" + "=" * 70)
        print(f"✅ Scraping completed!")
        print(f"   Total posts: {len(posts)}")
        print(f"   - Regular posts: {post_count}")
        print(f"   - Videos: {video_count}")
        print(f"   - Reels: {reel_count}")
        print(f"   Total comments: {total_comments}")
        print(f"   Output file: {output_file}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔒 Closing browser...")
        driver.quit()


if __name__ == '__main__':
    main()
