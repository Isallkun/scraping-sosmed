# Instagram Comment Scraping Guide

This guide explains how to scrape Instagram posts with comments for sentiment analysis.

## Overview

The Instagram scraper now supports:
- ✅ Post scraping from profiles
- ✅ Comment scraping from each post
- ✅ Organized output folder structure
- ✅ Configurable comment limits
- ✅ Sentiment analysis ready format

## Quick Start

### 1. Basic Scraping (with comments)

```bash
python scrape_instagram_simple.py
```

This will:
- Use default target from `.env` file
- Scrape 5 posts
- Get up to 20 comments per post
- Save to `output/instagram/posts_TIMESTAMP.json`

### 2. Custom Target and Limit

```bash
python scrape_instagram_simple.py https://www.instagram.com/username/ 10
```

Parameters:
- `username/` - Instagram profile URL
- `10` - Number of posts to scrape

### 3. Scrape Without Comments (faster)

```bash
python scrape_instagram_simple.py https://www.instagram.com/username/ 5 false false
```

Parameters:
- `false` (3rd param) - Headless mode (false = show browser)
- `false` (4th param) - Scrape comments (false = skip comments)

### 4. Advanced: Custom Comment Limit

```bash
python scrape_instagram_simple.py https://www.instagram.com/username/ 5 false true 50
```

Parameters:
- `5` - Posts to scrape
- `false` - Show browser
- `true` - Scrape comments
- `50` - Comments per post

## Output Structure

### File Location

All Instagram outputs are saved to:
```
output/instagram/posts_YYYYMMDD_HHMMSS.json
```

### Output Format

```json
{
  "metadata": {
    "platform": "instagram",
    "scraped_at": "2026-02-09T12:00:00Z",
    "target_url": "https://www.instagram.com/username/",
    "total_posts": 5,
    "total_comments": 87,
    "scrape_comments": true,
    "comments_per_post": 20
  },
  "posts": [
    {
      "post_id": "ABC123",
      "post_url": "https://www.instagram.com/p/ABC123/",
      "author": "username",
      "content": "This is the post caption #hashtag",
      "timestamp": "2026-02-09T10:00:00Z",
      "likes": 150,
      "comments_count": 18,
      "comments": [
        {
          "author": "user1",
          "text": "Great post! Love it!",
          "likes": 5,
          "timestamp": "2026-02-09T10:05:00Z"
        },
        {
          "author": "user2",
          "text": "Amazing content",
          "likes": 2,
          "timestamp": "2026-02-09T10:10:00Z"
        }
      ],
      "hashtags": ["hashtag"]
    }
  ]
}
```

## Sentiment Analysis

After scraping posts with comments, analyze sentiment:

```bash
python -m sentiment.main_analyzer --input output/instagram/posts_20260209_120000.json --output output/sentiment/posts_20260209_120000_sentiment.json
```

This will:
- Analyze sentiment of post captions
- Analyze sentiment of all comments
- Add sentiment scores to each post and comment
- Save results to `output/sentiment/`

### Sentiment Output Format

Each post and comment will have added fields:
```json
{
  "text": "Great post!",
  "sentiment": {
    "label": "positive",
    "score": 0.85,
    "compound": 0.72,
    "positive": 0.80,
    "neutral": 0.15,
    "negative": 0.05
  }
}
```

## Use Cases

### 1. Brand Monitoring

Track sentiment about your brand:
```bash
# Scrape your brand's Instagram
python scrape_instagram_simple.py https://www.instagram.com/yourbrand/ 50 false true 30

# Analyze sentiment
python -m sentiment.main_analyzer --input output/instagram/posts_*.json --output output/sentiment/brand_sentiment.json
```

### 2. Competitor Analysis

Monitor competitor engagement:
```bash
python scrape_instagram_simple.py https://www.instagram.com/competitor/ 30 true true 50
```

### 3. Influencer Research

Analyze influencer content and engagement:
```bash
python scrape_instagram_simple.py https://www.instagram.com/influencer/ 20 false true 100
```

## Tips & Best Practices

### 1. Rate Limiting

Instagram may block if you scrape too fast:
- Start with small limits (5-10 posts)
- Use headless=false initially to monitor
- Add delays between runs
- Don't scrape same profile repeatedly

### 2. Comment Quality

To get high-quality comments:
- Set `comments_per_post` higher (50-100)
- The scraper loads more comments by clicking "Load more"
- Recent posts usually have more comments available

### 3. Performance

**Fast scraping** (no comments):
```bash
python scrape_instagram_simple.py <url> 20 true false
# ~30 seconds for 20 posts
```

**Detailed scraping** (with comments):
```bash
python scrape_instagram_simple.py <url> 10 false true 50
# ~5-10 minutes for 10 posts with comments
```

### 4. Error Handling

If scraping fails:
1. Check Instagram login credentials in `.env`
2. Try with `headless=false` to see browser
3. Check if profile is public
4. Reduce number of posts/comments
5. Check logs in `logs/` folder

## Folder Organization

Keep outputs organized:

```bash
# Organize old files
python organize_outputs.py

# View folder structure
ls -la output/instagram/
ls -la output/sentiment/
```

## Advanced: Using the Scraper Class

For programmatic use:

```python
from scraper.scrapers.instagram import InstagramScraper

scraper = InstagramScraper(
    credentials={'username': 'user', 'password': 'pass'},
    headless=False
)

# Authenticate
scraper.authenticate()

# Scrape posts
posts = scraper.scrape_posts('https://instagram.com/profile/', limit=10)

# Scrape comments for a specific post
comments = scraper.scrape_post_comments(
    'https://instagram.com/p/POST_ID/',
    limit=50
)

# Cleanup
scraper.cleanup()
```

## Troubleshooting

### No Comments Found

**Problem**: `comments_count: 0` in output

**Solutions**:
1. Check if posts have comments
2. Increase wait time in code
3. Try with `headless=false` to debug
4. Some posts may have comments disabled

### Login Failed

**Problem**: Cannot login to Instagram

**Solutions**:
1. Verify credentials in `.env`
2. Check for 2FA (may need to disable)
3. Try logging in manually in browser first
4. Instagram may be blocking automation

### Scraping Too Slow

**Problem**: Takes too long to scrape

**Solutions**:
1. Reduce `comments_per_post` limit
2. Reduce number of posts
3. Set `scrape_comments=false` for faster scraping
4. Use `headless=true` for better performance

## Next Steps

After scraping Instagram comments:

1. **View Results**:
   ```bash
   python view_results.py output/instagram/posts_*.json
   ```

2. **Analyze Sentiment**:
   ```bash
   python -m sentiment.main_analyzer --input output/instagram/posts_*.json
   ```

3. **Export to Database**:
   ```bash
   python -m database.db_operations --import output/instagram/posts_*.json
   ```

4. **Create Reports**:
   - Use the sentiment analysis results
   - Calculate average sentiment scores
   - Identify most positive/negative comments
   - Track engagement metrics

## Example Workflow

Complete workflow for brand sentiment analysis:

```bash
# 1. Scrape posts with comments
python scrape_instagram_simple.py https://www.instagram.com/yourbrand/ 30 false true 50

# 2. Analyze sentiment
python -m sentiment.main_analyzer \
  --input output/instagram/posts_20260209_120000.json \
  --output output/sentiment/brand_sentiment.json

# 3. View results
python view_results.py output/sentiment/brand_sentiment.json

# 4. (Optional) Import to database for further analysis
python -m database.db_operations --import output/sentiment/brand_sentiment.json
```

---

**Need Help?**
- Check `docs/TROUBLESHOOTING.md`
- View logs in `logs/`
- See examples in `examples/`
