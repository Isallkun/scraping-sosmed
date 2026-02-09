# Design Document: Instagram Reel Support & Comment Extraction Enhancement

## Overview

Enhancement ini menambahkan dua fitur utama ke `scrape_instagram_simple.py`:

1. **Reel Support**: Mendeteksi dan scrape Instagram Reels selain posts reguler
2. **Improved Comment Extraction**: Mengambil teks komentar aktual dengan 3 strategi fallback

File yang dimodifikasi: `scrape_instagram_simple.py`

## Architecture Changes

### Current Flow
```
Profile Page → Find /p/ links → Extract post data → Get comment count (meta tag)
```

### Enhanced Flow
```
Profile Page → Find /p/ AND /reel/ links → Extract post data + post_type
              ↓
              Determine post_type from URL
              ↓
              Enhanced comment extraction (3 strategies):
              1. Page source JSON parsing
              2. DOM extraction with WebDriverWait
              3. JavaScript DOM query fallback
```

## Component Modifications

### 1. Reel Support in `scrape_profile_simple()`

**Location**: Lines ~436-527

**Changes**:

#### A. Update Link Selectors (line ~447-450)

**Before**:
```python
post_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/p/"]')
```

**After**:
```python
# Find both posts and reels
post_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/p/"], a[href*="/reel/"]')
```

#### B. Extract post_type from URL (line ~462-467)

**Before**:
```python
post_id = href.split('/p/')[1].split('/')[0]
unique_posts.add((post_id, href))
```

**After**:
```python
# Determine post type and extract ID
if '/p/' in href:
    post_id = href.split('/p/')[1].split('/')[0]
    post_type = 'post'
elif '/reel/' in href:
    post_id = href.split('/reel/')[1].split('/')[0]
    post_type = 'reel'
else:
    continue  # Skip unknown types

unique_posts.add((post_id, href, post_type))
```

#### C. Pass post_type Through Pipeline

**Tuple structure change**:
- Before: `(post_id, href)`
- After: `(post_id, href, post_type)`

**Add to post_data dict**:
```python
post_data = {
    'post_id': post_id,
    'post_type': post_type,  # NEW FIELD
    'platform': 'instagram',
    'author': profile_username,
    # ... rest of fields
}
```

#### D. Update Metadata Output

**Add counts**:
```python
metadata = {
    'platform': 'instagram',
    'target_url': profile_url,
    'total_posts': len(all_posts),
    'post_count': sum(1 for p in all_posts if p.get('post_type') == 'post'),
    'reel_count': sum(1 for p in all_posts if p.get('post_type') == 'reel'),
    'scraped_at': datetime.now().isoformat()
}
```

### 2. Enhanced Comment Extraction in `scrape_comments_from_post()`

**Location**: Lines ~305-433

**Complete Rewrite with 3 Strategies**:

#### Strategy 1: Page Source JSON (Existing - Keep)

Parse `window._sharedData` or `__additionalDataLoaded` from page source.

**Keep existing implementation** for backward compatibility with older Instagram pages.

#### Strategy 2: DOM Extraction (Major Rewrite)

**New Implementation**:

```python
def scrape_comments_from_post_dom(driver, post_url, post_type='post'):
    """
    Strategy 2: DOM-based comment extraction with WebDriverWait
    
    Args:
        driver: Selenium WebDriver instance
        post_url: URL of the post/reel
        post_type: 'post' or 'reel' for logging
    
    Returns:
        list: Array of comment objects with text, author, timestamp
    """
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    comments = []
    
    try:
        # Wait for comment section to render
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'ul'))
        )
        time.sleep(2)  # Additional wait for dynamic content
        
        # Try to click "View all comments" button
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
        
        # Scroll and load more comments (up to 5 times)
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
        
        # Extract comment elements
        comment_elements = driver.find_elements(By.CSS_SELECTOR, 'ul li')
        
        for elem in comment_elements:
            try:
                # Extract author from link
                author_elem = elem.find_element(By.CSS_SELECTOR, 'a[href^="/"]')
                author = author_elem.get_attribute('href').strip('/').split('/')[0]
                
                # Extract comment text from span with dir="auto"
                text_elem = elem.find_element(By.CSS_SELECTOR, 'span[dir="auto"]')
                text = text_elem.text.strip()
                
                # Skip if text is empty or looks like UI text
                if not text or len(text) < 2:
                    continue
                
                # Skip captions (usually the first element with author matching profile)
                if 'Original audio' in text or 'Suara asli' in text:
                    continue
                
                # Extract timestamp if available
                timestamp = None
                try:
                    time_elem = elem.find_element(By.TAG_NAME, 'time')
                    timestamp = time_elem.get_attribute('datetime')
                except:
                    pass
                
                comment_obj = {
                    'author': author,
                    'text': text,
                    'timestamp': timestamp
                }
                
                comments.append(comment_obj)
                
            except Exception as e:
                continue  # Skip malformed comments
        
        print(f"  ✓ Extracted {len(comments)} comments via DOM")
        
    except Exception as e:
        print(f"  ✗ DOM extraction failed: {str(e)}")
    
    return comments
```

#### Strategy 3: JavaScript DOM Query (New Fallback)

**New Implementation**:

```python
def scrape_comments_from_post_js(driver, post_url, post_type='post'):
    """
    Strategy 3: JavaScript-based DOM query fallback
    
    Uses execute_script to query DOM directly from browser context.
    Can access elements that Selenium sometimes misses.
    
    Args:
        driver: Selenium WebDriver instance
        post_url: URL of the post/reel
        post_type: 'post' or 'reel' for logging
    
    Returns:
        list: Array of comment objects
    """
    comments = []
    
    try:
        # JavaScript to extract comments directly from DOM
        js_script = """
        const comments = [];
        const commentElements = document.querySelectorAll('ul li');
        
        commentElements.forEach(elem => {
            try {
                const authorLink = elem.querySelector('a[href^="/"]');
                const textSpan = elem.querySelector('span[dir="auto"]');
                const timeElem = elem.querySelector('time');
                
                if (authorLink && textSpan) {
                    const author = authorLink.getAttribute('href').replace('/', '').split('/')[0];
                    const text = textSpan.textContent.trim();
                    const timestamp = timeElem ? timeElem.getAttribute('datetime') : null;
                    
                    if (text && text.length > 2) {
                        comments.push({
                            author: author,
                            text: text,
                            timestamp: timestamp
                        });
                    }
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
```

#### Orchestrator Function

**Update main comment extraction function**:

```python
def scrape_comments_from_post(driver, post_url, post_type='post'):
    """
    Extract comments using multiple strategies with fallback.
    
    Tries 3 strategies in order:
    1. Page source JSON parsing (existing)
    2. DOM extraction with WebDriverWait
    3. JavaScript DOM query
    
    Args:
        driver: Selenium WebDriver instance
        post_url: URL of the post/reel
        post_type: 'post' or 'reel' for logging context
    
    Returns:
        list: Array of comment objects
    """
    print(f"\n  Extracting comments from {post_type}: {post_url}")
    
    # Strategy 1: Page source JSON (existing implementation)
    comments = scrape_comments_from_post_json(driver, post_url)
    if comments:
        return comments
    
    # Strategy 2: DOM extraction
    comments = scrape_comments_from_post_dom(driver, post_url, post_type)
    if comments:
        return comments
    
    # Strategy 3: JavaScript fallback
    comments = scrape_comments_from_post_js(driver, post_url, post_type)
    if comments:
        return comments
    
    print(f"  ⚠ All comment extraction strategies failed")
    return []
```

### 3. Output Schema Changes

**Enhanced Post Object**:

```json
{
  "post_id": "abc123",
  "post_type": "reel",
  "platform": "instagram",
  "author": "username",
  "content": "Caption text here",
  "timestamp": "2024-01-15T10:30:00Z",
  "likes": 150,
  "comments_count": 25,
  "url": "https://instagram.com/reel/abc123",
  "comments": [
    {
      "author": "commenter1",
      "text": "Great reel!",
      "timestamp": "2024-01-15T11:00:00Z"
    },
    {
      "author": "commenter2",
      "text": "Love this content",
      "timestamp": "2024-01-15T11:30:00Z"
    }
  ]
}
```

**Enhanced Metadata**:

```json
{
  "platform": "instagram",
  "target_url": "https://instagram.com/username",
  "total_posts": 10,
  "post_count": 6,
  "reel_count": 4,
  "scraped_at": "2024-01-15T12:00:00Z"
}
```

## Error Handling

### Reel Detection Errors
- If URL format is neither `/p/` nor `/reel/`, skip the item
- Log warning for unknown URL patterns
- Continue processing remaining items

### Comment Extraction Errors
- Each strategy has independent try-catch blocks
- Failures in one strategy don't prevent trying next strategy
- Log which strategy succeeded or if all failed
- Return empty array if all strategies fail (graceful degradation)

### Timeout Handling
- WebDriverWait timeout: 10 seconds for comment section
- Additional sleep: 2 seconds for dynamic content
- Load more attempts: Maximum 5 iterations
- Each scroll/click has 1-2 second delay

## Testing Strategy

### Unit Tests
- Test post_type extraction from various URL formats
- Test comment object structure validation
- Test metadata count calculations

### Integration Tests
- Test scraping profile with mix of posts and reels
- Test comment extraction on posts with many comments
- Test fallback behavior when strategies fail
- Test Indonesian locale support

### Manual Verification
1. Run: `python scrape_instagram_simple.py https://www.instagram.com/rusdi_sutejo/ 3`
2. Verify output JSON has:
   - Mix of `post_type: "post"` and `post_type: "reel"`
   - Non-empty `comments` arrays with actual text
   - Correct `post_count` and `reel_count` in metadata
3. Run sentiment analysis on output
4. Verify existing tests still pass

## Performance Considerations

- Comment extraction adds 2-10 seconds per post (depending on comment count)
- Load more iterations limited to 5 to prevent excessive delays
- WebDriverWait prevents indefinite blocking
- Graceful fallback ensures scraping continues even if comments fail

## Backward Compatibility

- Existing posts without `post_type` field remain valid
- Empty `comments` array is valid (backward compatible)
- All existing functionality preserved
- No breaking changes to output schema (only additions)
