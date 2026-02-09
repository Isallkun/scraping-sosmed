# Quick Start Guide - Social Media Scraper

## Prerequisites

✅ Python 3.11+ installed
✅ Chrome/Chromium browser installed
✅ Dependencies installed (`pip install -r requirements.txt`)
✅ `.env` file configured with your credentials

## Quick Commands

### 1. Run Instagram Scraper (Easy Way)

```bash
# Windows
run_scraper.bat

# Or with custom parameters
run_scraper.bat instagram "https://www.instagram.com/username/" 20
```

### 2. Run Scraper (Manual Way)

```bash
# Scrape Instagram profile (10 posts, visible browser)
python -m scraper.main_scraper --target "https://www.instagram.com/rusdi_sutejo/" --limit 10 --no-headless

# Scrape Instagram profile (50 posts, headless mode)
python -m scraper.main_scraper --target "https://www.instagram.com/rusdi_sutejo/" --limit 50 --headless

# Scrape with custom output file
python -m scraper.main_scraper --target "https://www.instagram.com/rusdi_sutejo/" --limit 20 --output my_posts.json
```

### 3. Run Sentiment Analysis

```bash
# Windows (Easy Way)
run_sentiment.bat output\instagram_posts_20260209_083312.json

# Manual Way
python -m sentiment.main_analyzer --input output\instagram_posts_20260209_083312.json --output output\posts_with_sentiment.json --model vader
```

### 4. View Results

Results are saved in the `output/` directory:
- Scraped data: `output/instagram_posts_YYYYMMDD_HHMMSS.json`
- With sentiment: `output/instagram_posts_YYYYMMDD_HHMMSS_sentiment.json`

## Configuration

Edit `.env` file to change settings:

```env
# Platform
SCRAPER_PLATFORM=instagram

# Credentials
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Target
INSTAGRAM_TARGET_URL=https://www.instagram.com/username/

# Settings
SCRAPER_MAX_POSTS=100
SCRAPER_RATE_LIMIT=30
SCRAPER_HEADLESS=true
```

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'scraper'"
**Solution**: Run as module: `python -m scraper.main_scraper` instead of `python scraper/main_scraper.py`

### Issue: "ChromeDriver not found"
**Solution**: 
1. Download ChromeDriver from https://chromedriver.chromium.org/
2. Add to PATH or place in project directory

### Issue: "Login failed"
**Solution**: 
1. Check credentials in `.env` file
2. Try running with `--no-headless` to see what's happening
3. Instagram may require 2FA - disable it temporarily

### Issue: Browser opens but nothing happens
**Solution**: 
1. Check your internet connection
2. Instagram may be blocking automated access
3. Try reducing `SCRAPER_RATE_LIMIT` to 20 or lower

## Output Format

### Scraped Data (JSON)
```json
{
  "metadata": {
    "platform": "instagram",
    "scraped_at": "2026-02-09T08:33:12Z",
    "target_url": "https://www.instagram.com/rusdi_sutejo/",
    "total_posts": 10
  },
  "posts": [
    {
      "post_id": "abc123",
      "author": "rusdi_sutejo",
      "content": "Post content here...",
      "timestamp": "2026-02-08T10:30:00Z",
      "likes": 150,
      "comments_count": 25,
      "hashtags": ["#example", "#instagram"]
    }
  ]
}
```

### With Sentiment Analysis
```json
{
  "metadata": { ... },
  "posts": [
    {
      "post_id": "abc123",
      "content": "Post content here...",
      "sentiment": {
        "label": "positive",
        "scores": {
          "positive": 0.75,
          "negative": 0.05,
          "neutral": 0.20,
          "compound": 0.70
        }
      }
    }
  ]
}
```

## Next Steps

1. **Database Storage**: Set up PostgreSQL and run migrations
2. **Automation**: Set up n8n workflows for scheduled scraping
3. **Docker**: Deploy using Docker Compose for production

See `README.md` for full documentation.

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Run with `--log-level DEBUG` for detailed output
3. Review `README.md` and `ARCHITECTURE.md`
