# Usage Guide - Social Media Scraper Automation

## 🚀 Quick Start

### Option 1: Demo Mode (Recommended for Testing)

```bash
# 1. Generate demo data
python demo_scraper.py

# 2. Run sentiment analysis
python -m sentiment.main_analyzer --input output/demo_instagram_posts_TIMESTAMP.json --output output/demo_instagram_posts_TIMESTAMP_sentiment.json --model vader

# 3. View results
python view_results.py output/demo_instagram_posts_TIMESTAMP_sentiment.json
```

### Option 2: Real Scraping (Requires Valid Credentials)

```bash
# 1. Configure .env file with your credentials
# Edit INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD

# 2. Run scraper (visible browser for debugging)
python -m scraper.main_scraper --target "https://www.instagram.com/username/" --limit 10 --no-headless

# 3. Run scraper (headless mode for production)
python -m scraper.main_scraper --target "https://www.instagram.com/username/" --limit 50 --headless

# 4. Run sentiment analysis
python -m sentiment.main_analyzer --input output/instagram_posts_TIMESTAMP.json --output output/instagram_posts_TIMESTAMP_sentiment.json --model vader

# 5. View results
python view_results.py output/instagram_posts_TIMESTAMP_sentiment.json
```

## 📁 Available Scripts

### 1. `demo_scraper.py` - Generate Demo Data
Creates sample Instagram posts for testing sentiment analysis without real scraping.

```bash
python demo_scraper.py
```

**Output**: `output/demo_instagram_posts_TIMESTAMP.json`

### 2. `scrape_instagram_simple.py` - Instagram Scraping (Enhanced)
Scrapes Instagram posts and reels with enhanced comment extraction.

```bash
# Basic usage - scrape 10 posts/reels
python scrape_instagram_simple.py https://www.instagram.com/username/ 10

# Scrape without comments (faster)
python scrape_instagram_simple.py https://www.instagram.com/username/ 10 --no-comments

# Scrape with more comments per post
python scrape_instagram_simple.py https://www.instagram.com/username/ 5 --max-comments 50
```

**Features**:
- ✅ Detects and scrapes both posts (`/p/`) and reels (`/reel/`)
- ✅ Extracts post content, likes, comment count
- ✅ Enhanced comment extraction with 3-strategy fallback
- ✅ Supports Indonesian and English UI
- ✅ Graceful error handling and rate limiting

**Output**: `output/instagram/posts_TIMESTAMP.json`

### 3. `scraper/main_scraper.py` - Real Scraping (Legacy)
Legacy scraper for other platforms (Twitter, Facebook).

```bash
# Basic usage
python -m scraper.main_scraper --target URL --limit NUMBER

# With all options
python -m scraper.main_scraper \
  --platform instagram \
  --target "https://www.instagram.com/username/" \
  --limit 50 \
  --output custom_output.json \
  --headless \
  --log-level INFO
```

**Parameters**:
- `--platform`: Platform to scrape (instagram, twitter, facebook)
- `--target`: Target URL (profile, hashtag, etc.)
- `--limit`: Maximum number of posts to scrape
- `--output`: Custom output file path
- `--headless`: Run browser in headless mode
- `--no-headless`: Run browser with visible UI (for debugging)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)

### 4. `sentiment/main_analyzer.py` - Sentiment Analysis
Analyzes sentiment of scraped posts.

```bash
python -m sentiment.main_analyzer \
  --input INPUT_FILE.json \
  --output OUTPUT_FILE.json \
  --model vader \
  --batch-size 100
```

**Parameters**:
- `--input`: Input JSON file with scraped posts
- `--output`: Output JSON file with sentiment results
- `--model`: Sentiment model (vader or textblob)
- `--batch-size`: Batch size for processing

### 4. `view_results.py` - View Results
Displays sentiment analysis results in a readable format.

```bash
python view_results.py OUTPUT_FILE.json
```

## 🎯 Complete Workflow Examples

### Example 1: Demo Workflow (No Credentials Needed)

```bash
# Step 1: Generate demo data
python demo_scraper.py

# Step 2: Analyze sentiment
python -m sentiment.main_analyzer \
  --input output/demo_instagram_posts_20260209_083538.json \
  --output output/demo_instagram_posts_20260209_083538_sentiment.json \
  --model vader

# Step 3: View results
python view_results.py output/demo_instagram_posts_20260209_083538_sentiment.json
```

### Example 2: Instagram Profile Scraping (Enhanced with Comments)

```bash
# Step 1: Scrape Instagram profile with comments (10 posts/reels)
python scrape_instagram_simple.py https://www.instagram.com/rusdi_sutejo/ 10

# Step 2: Analyze sentiment (includes comment sentiment)
python -m sentiment.main_analyzer \
  --input output/instagram/posts_20260209_093833.json \
  --output output/instagram/posts_20260209_093833_sentiment.json \
  --model vader

# Step 3: View results
python view_results.py output/instagram/posts_20260209_093833_sentiment.json
```

**What you get**:
- Mix of posts and reels (automatically detected)
- Post captions and metadata (likes, comment counts)
- Actual comment text with authors and timestamps
- Separate counts for posts vs reels in metadata
- Sentiment analysis on both posts and comments

### Example 3: Fast Scraping Without Comments

```bash
# Scrape 20 posts/reels quickly (no comment extraction)
python scrape_instagram_simple.py https://www.instagram.com/username/ 20 --no-comments

# Analyze sentiment
python -m sentiment.main_analyzer \
  --input output/instagram/posts_TIMESTAMP.json \
  --output output/instagram/posts_TIMESTAMP_sentiment.json \
  --model vader
```

**Performance**: ~2-3 seconds per post (vs 5-15 seconds with comments)

### Example 4: Deep Comment Extraction

```bash
# Extract up to 50 comments per post (more scrolling/loading)
python scrape_instagram_simple.py https://www.instagram.com/username/ 5 --max-comments 50

# This will:
# - Scroll more times in comment section
# - Click "Load more" more frequently
# - Take longer but get more comments
```

### Example 5: Batch Processing Multiple Files

```bash
# Analyze all scraped files
for file in output/instagram_posts_*.json; do
  python -m sentiment.main_analyzer \
    --input "$file" \
    --output "${file%.json}_sentiment.json" \
    --model vader
done
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Scraper Settings
SCRAPER_PLATFORM=instagram
SCRAPER_RATE_LIMIT=30
SCRAPER_MAX_POSTS=100
SCRAPER_TIMEOUT=300
SCRAPER_HEADLESS=true
SCRAPER_LOG_LEVEL=INFO

# Instagram Credentials
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
INSTAGRAM_TARGET_URL=https://www.instagram.com/username/

# Sentiment Analysis
SENTIMENT_MODEL=vader
SENTIMENT_BATCH_SIZE=100

# Database (Optional)
DATABASE_URL=postgresql://user:pass@localhost:5432/social_scraper
```

## 📊 Output Format

### Enhanced Scraped Data (Instagram)

The Instagram scraper now outputs enhanced data with post type detection and comment extraction:

```json
{
  "metadata": {
    "platform": "instagram",
    "scraped_at": "2026-02-09T02:38:33.302169Z",
    "target_url": "https://www.instagram.com/username/",
    "total_posts": 10,
    "post_count": 6,
    "reel_count": 4,
    "total_comments": 25,
    "scrape_comments": true,
    "comments_per_post": 20,
    "method": "enhanced with comments"
  },
  "posts": [
    {
      "post_id": "ABC123xyz",
      "post_type": "post",
      "post_url": "https://www.instagram.com/username/p/ABC123xyz/",
      "author": "username",
      "content": "Post caption text here...",
      "timestamp": "2026-02-09T09:38:10.803159Z",
      "likes": 146,
      "comments_count": 5,
      "comments": [
        {
          "author": "commenter1",
          "text": "Great post!",
          "timestamp": "2026-02-09T10:00:00Z"
        },
        {
          "author": "commenter2",
          "text": "Love this content!",
          "timestamp": "2026-02-09T10:15:00Z"
        }
      ],
      "hashtags": ["#example", "#instagram"],
      "scraped_at": "2026-02-09T09:38:10.803159Z"
    },
    {
      "post_id": "XYZ789abc",
      "post_type": "reel",
      "post_url": "https://www.instagram.com/username/reel/XYZ789abc/",
      "author": "username",
      "content": "Reel caption...",
      "timestamp": "2026-02-09T08:20:00.000000Z",
      "likes": 523,
      "comments_count": 12,
      "comments": [
        {
          "author": "fan123",
          "text": "Amazing reel!",
          "timestamp": "2026-02-09T08:30:00Z"
        }
      ],
      "hashtags": ["#reels", "#viral"],
      "scraped_at": "2026-02-09T09:38:20.000000Z"
    }
  ]
}
```

### New Fields Explained

#### Post Object Fields
- **`post_type`**: `"post"` or `"reel"` - Automatically detected from URL pattern
  - Posts have URL pattern: `/p/{id}`
  - Reels have URL pattern: `/reel/{id}`
- **`comments`**: Array of comment objects (empty if extraction fails or disabled)
  - Each comment has: `author`, `text`, `timestamp` (optional)
  - Comments are extracted using 3-strategy fallback for reliability

#### Metadata Fields
- **`post_count`**: Number of regular posts scraped
- **`reel_count`**: Number of reels scraped
- **`total_comments`**: Total comments extracted across all posts/reels
- **`scrape_comments`**: Boolean indicating if comment extraction was enabled
- **`comments_per_post`**: Maximum comments attempted per post/reel

### Comment Extraction Details

The scraper uses **3 strategies** to extract comments, trying each in order:

1. **Strategy 1: Page Source JSON Parsing**
   - Fastest method
   - Parses embedded JSON from `window._sharedData` or `__additionalDataLoaded`
   - Works on older Instagram page versions

2. **Strategy 2: DOM Extraction with WebDriverWait**
   - Most reliable for current Instagram UI
   - Waits for comment section to render
   - Clicks "View all comments" button (English/Indonesian)
   - Scrolls and clicks "Load more" up to 5 times
   - Filters out captions and UI text

3. **Strategy 3: JavaScript DOM Query Fallback**
   - Last resort method
   - Uses `execute_script()` to query DOM directly
   - Can access elements Selenium sometimes misses

**Graceful Degradation**: If all strategies fail, returns empty `comments` array and continues scraping.

### Sentiment Analysis Results
```json
{
  "metadata": {
    "analyzed_at": "2026-02-09T08:36:08Z",
    "sentiment_model": "vader",
    "error_count": 0
  },
  "posts": [
    {
      "post_id": "abc123",
      "content": "Post content...",
      "sentiment": {
        "label": "positive",
        "score": 0.757,
        "compound": 0.757,
        "positive": 0.555,
        "neutral": 0.445,
        "negative": 0.0,
        "model": "vader"
      }
    }
  ]
}
```

## 🐛 Troubleshooting

### Issue: Authentication Timeout

**Symptoms**: 
```
ERROR - Authentication timeout: Message: ...
```

**Solutions**:
1. Run with `--no-headless` to see what's happening
2. Check credentials in `.env` file
3. Instagram may require 2FA - disable temporarily
4. Try increasing timeout in `.env`: `SCRAPER_TIMEOUT=600`
5. Instagram may be blocking automated access - try later

### Issue: No Comments Extracted

**Symptoms**:
- `comments` array is empty `[]`
- Console shows "All comment extraction strategies failed"

**Solutions**:
1. **Check if post has comments**: Some posts genuinely have no comments
2. **Instagram UI changes**: Instagram frequently updates their UI, breaking selectors
3. **Rate limiting**: Instagram may be blocking comment access
4. **Try different strategy**:
   ```bash
   # Check console output to see which strategy failed
   # Strategy 1: JSON parsing (fastest)
   # Strategy 2: DOM extraction (most reliable)
   # Strategy 3: JavaScript fallback (last resort)
   ```
5. **Increase wait time**: Instagram may need more time to load comments
6. **Check language**: Scraper supports English and Indonesian - other languages may need selector updates

### Issue: Missing post_type Field

**Symptoms**:
- Output JSON doesn't have `post_type` field
- Or `post_type` is always `null`

**Solutions**:
1. **Update scraper**: Make sure you're using the latest version
2. **Check URL format**: Only `/p/` and `/reel/` URLs are supported
3. **Verify implementation**: Check that `post_type` logic is in `scrape_profile_simple()`

### Issue: Reels Not Being Scraped

**Symptoms**:
- `reel_count` is 0 in metadata
- Only posts are scraped, no reels

**Solutions**:
1. **Check profile**: Profile may not have any reels
2. **Verify selector**: Ensure link selector includes `a[href*="/reel/"]`
3. **Instagram UI changes**: Instagram may have changed reel URL patterns
4. **Check console output**: Look for "Reel X/Y" messages

### Issue: ChromeDriver Not Found

**Symptoms**:
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**Solutions**:
1. Download ChromeDriver: https://chromedriver.chromium.org/
2. Add to system PATH
3. Or place in project directory

### Issue: Rate Limiting / IP Blocking

**Symptoms**:
- Slow scraping
- Frequent errors
- "Too many requests" messages

**Solutions**:
1. Reduce `SCRAPER_RATE_LIMIT` to 20 or lower
2. Add delays between scraping sessions
3. Use residential proxies (advanced)
4. Respect platform rate limits

### Issue: Module Not Found

**Symptoms**:
```
ModuleNotFoundError: No module named 'scraper'
```

**Solutions**:
1. Always run as module: `python -m scraper.main_scraper`
2. Don't use: `python scraper/main_scraper.py`
3. Ensure you're in project root directory

## 📈 Performance Tips

1. **Start Small**: Test with `--limit 5` first
2. **Use Headless Mode**: Faster scraping with `--headless`
3. **Batch Processing**: Process multiple files at once
4. **Rate Limiting**: Respect platform limits to avoid blocks
5. **Error Handling**: Check logs in `logs/` directory

## 🔐 Security Best Practices

1. **Never commit .env**: Already in .gitignore
2. **Use app passwords**: For email notifications
3. **Rotate credentials**: Change passwords regularly
4. **Monitor logs**: Check for suspicious activity
5. **Respect TOS**: Follow platform terms of service

## 📚 Additional Resources

- **Full Documentation**: See `README.md`
- **Architecture**: See `ARCHITECTURE.md`
- **API Reference**: See `API.md`
- **Security Guide**: See `SECURITY.md`
- **Quick Start**: See `QUICKSTART.md`

## 💡 Tips & Tricks

### Tip 1: Debug Comment Extraction
```bash
# Watch the browser to see comment extraction in action
python scrape_instagram_simple.py URL 3 --visible

# Check console output for strategy success/failure:
# ✓ Strategy 1 succeeded: Extracted N comments via JSON
# ✓ Strategy 2 succeeded: Extracted N comments via DOM
# ✓ Strategy 3 succeeded: Extracted N comments via JavaScript
# ⚠ All comment extraction strategies failed
```

### Tip 2: Optimize for Speed vs Depth
```bash
# Fast scraping (no comments): ~2-3 sec/post
python scrape_instagram_simple.py URL 20 --no-comments

# Balanced (default, 20 comments): ~5-8 sec/post
python scrape_instagram_simple.py URL 10

# Deep extraction (50 comments): ~10-15 sec/post
python scrape_instagram_simple.py URL 5 --max-comments 50
```

### Tip 3: Filter by Post Type
```bash
# After scraping, filter posts vs reels using jq
jq '.posts[] | select(.post_type == "post")' output.json
jq '.posts[] | select(.post_type == "reel")' output.json

# Or in Python:
posts = [p for p in data['posts'] if p['post_type'] == 'post']
reels = [p for p in data['posts'] if p['post_type'] == 'reel']
```

### Tip 4: Analyze Comment Sentiment Separately
```bash
# Extract all comments from scraped data
import json

with open('output.json') as f:
    data = json.load(f)

all_comments = []
for post in data['posts']:
    for comment in post.get('comments', []):
        all_comments.append({
            'post_id': post['post_id'],
            'post_type': post['post_type'],
            'comment_author': comment['author'],
            'comment_text': comment['text']
        })

# Now analyze comment sentiment separately
```

### Tip 5: Monitor Extraction Success Rate
```bash
# Check metadata for extraction statistics
jq '.metadata | {total_posts, post_count, reel_count, total_comments}' output.json

# Calculate comments per post
# total_comments / total_posts = average comments extracted
```

### Tip 6: Debug Mode
```bash
# Run with debug logging to see detailed information
python -m scraper.main_scraper \
  --target URL \
  --limit 5 \
  --no-headless \
  --log-level DEBUG
```

### Tip 2: Custom Output Directory
```bash
# Organize outputs by date
mkdir -p output/$(date +%Y-%m-%d)
python -m scraper.main_scraper \
  --target URL \
  --output output/$(date +%Y-%m-%d)/posts.json
```

### Tip 3: Compare Sentiment Models
```bash
# Analyze with both models
python -m sentiment.main_analyzer --input posts.json --output posts_vader.json --model vader
python -m sentiment.main_analyzer --input posts.json --output posts_textblob.json --model textblob
```

## 🎓 Learning Path

1. **Start with Demo**: Run `demo_scraper.py` to understand output format
2. **Test Sentiment**: Analyze demo data with sentiment analyzer
3. **View Results**: Use `view_results.py` to see insights
4. **Try Real Scraping**: Start with `--limit 5 --no-headless`
5. **Scale Up**: Increase limit and use headless mode
6. **Automate**: Set up n8n workflows for scheduling

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Run with `--log-level DEBUG`
3. Review this guide and `README.md`
4. Check GitHub issues

---

**Happy Scraping! 🚀**