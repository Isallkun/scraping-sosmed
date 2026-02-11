# Social Media Scraper - Quick Reference Card

## 🚀 Quick Start (3 Commands)

```bash
# 1. Generate demo data (safe, no login required)
python demo_scraper.py

# 2. Analyze sentiment
python -m sentiment.main_analyzer --input output/demo_instagram_posts_TIMESTAMP.json --output output/demo_instagram_posts_TIMESTAMP_sentiment.json

# 3. View results
python view_results.py output/demo_instagram_posts_TIMESTAMP_sentiment.json
```

---

## 📸 Real Instagram Scraping

### Setup (One Time)

Edit `.env` file:

```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

### Scrape Posts

```bash
# Scrape 5 posts (default)
python scrape_instagram_simple.py

# Scrape 3 posts from specific profile
python scrape_instagram_simple.py https://www.instagram.com/rusdi_sutejo/ 3

# Scrape in headless mode (background)
python scrape_instagram_simple.py https://www.instagram.com/rusdi_sutejo/ 10 true
```

---

## 🎭 Sentiment Analysis

```bash
# Analyze scraped data
python -m sentiment.main_analyzer --input output/instagram_simple_TIMESTAMP.json --output output/instagram_simple_TIMESTAMP_sentiment.json

# Use TextBlob instead of VADER
python -m sentiment.main_analyzer --input output/instagram_simple_TIMESTAMP.json --output output/instagram_simple_TIMESTAMP_sentiment.json --model textblob
```

---

## 👀 View Results

```bash
# View any JSON output file
python view_results.py output/instagram_simple_TIMESTAMP_sentiment.json

# View demo results
python view_results.py output/demo_instagram_posts_TIMESTAMP_sentiment.json
```

---

## 🔧 Batch Scripts (Windows)

```bash
# Quick scraping
run_scraper.bat

# Quick sentiment analysis
run_sentiment.bat output/instagram_simple_TIMESTAMP.json
```

---

## 🗄️ Database Management

### Clear Database

```bash
# Clear with confirmation (safe)
python scripts/clear_database.py

# Quick clear (no confirmation - for automation)
python scripts/clear_database_quick.py
```

### Flask Dashboard

```bash
# Start web dashboard
python run_flask.py

# Access at: http://127.0.0.1:5000
# Features:
# - View analytics
# - Scrape Instagram directly from UI
# - Import/Export data
# - Sentiment analysis charts
```

---

## 📊 Complete Workflow

```bash
# Step 1: Scrape
python scrape_instagram_simple.py https://www.instagram.com/rusdi_sutejo/ 10

# Step 2: Analyze (copy filename from Step 1)
python -m sentiment.main_analyzer --input output/instagram_simple_20260209_091108.json --output output/instagram_simple_20260209_091108_sentiment.json

# Step 3: View
python view_results.py output/instagram_simple_20260209_091108_sentiment.json
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_instagram_scraper.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=scraper --cov=sentiment
```

---

## 📁 Output Files

All output files are saved to `output/` directory:

- `instagram_simple_TIMESTAMP.json` - Scraped data
- `instagram_simple_TIMESTAMP_sentiment.json` - With sentiment analysis
- `demo_instagram_posts_TIMESTAMP.json` - Demo data
- `demo_instagram_posts_TIMESTAMP_sentiment.json` - Demo with sentiment

---

## 🔍 Logs

Check logs for debugging:

- `logs/scraper.instagram.log` - Instagram scraper logs
- `logs/scraper.twitter.log` - Twitter scraper logs
- `logs/scraper.facebook.log` - Facebook scraper logs

---

## ⚙️ Configuration

Edit `.env` file for settings:

```env
# Credentials
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Scraping settings
SCRAPER_HEADLESS=false          # true for background
SCRAPER_RATE_LIMIT=30           # requests per minute
SCRAPER_MAX_POSTS=100           # max posts per run
SCRAPER_TIMEOUT=300             # timeout in seconds

# Logging
SCRAPER_LOG_LEVEL=INFO          # DEBUG for more details

# Sentiment
SENTIMENT_MODEL=vader           # or textblob
```

---

## 🆘 Troubleshooting

### Login fails

```bash
# Run in visible mode to debug
python scrape_instagram_simple.py https://www.instagram.com/profile/ 5 false
```

### No posts found

- Check if profile is public
- Verify profile URL
- Try increasing limit

### Tests failing

```bash
# Check specific test
pytest tests/test_instagram_scraper.py -v

# View logs
type logs\scraper.instagram.log
```

---

## 📚 Documentation

- `README.md` - Project overview
- `docs/QUICKSTART.md` - Quick start guide
- `docs/USAGE_GUIDE.md` - Complete usage guide
- `docs/INSTAGRAM_SIMPLIFIED_GUIDE.md` - Instagram scraping guide
- `docs/REAL_SCRAPING_GUIDE.md` - Real scraping warnings
- `docs/TROUBLESHOOTING.md` - Troubleshooting guide
- `docs/REAL_SCRAPING_COMPLETION.md` - Completion summary

---

## ✅ Status Check

```bash
# Verify setup
python verify_setup.py

# Check Python version
python --version

# Check installed packages
pip list | findstr selenium
pip list | findstr vaderSentiment
pip list | findstr textblob
```

---

## 🎯 Common Use Cases

### 1. Daily Monitoring

```bash
# Scrape latest 10 posts daily
python scrape_instagram_simple.py https://www.instagram.com/target/ 10 true
```

### 2. Sentiment Tracking

```bash
# Scrape and analyze
python scrape_instagram_simple.py https://www.instagram.com/target/ 20
python -m sentiment.main_analyzer --input output/instagram_simple_TIMESTAMP.json --output output/instagram_simple_TIMESTAMP_sentiment.json
```

### 3. Demo/Testing

```bash
# Use demo data for testing
python demo_scraper.py
python -m sentiment.main_analyzer --input output/demo_instagram_posts_TIMESTAMP.json --output output/demo_instagram_posts_TIMESTAMP_sentiment.json
python view_results.py output/demo_instagram_posts_TIMESTAMP_sentiment.json
```

---

## 🔐 Security

- ✅ Never commit `.env` file
- ✅ Use `.env.example` as template
- ✅ Keep credentials secure
- ✅ Use strong passwords
- ✅ Enable 2FA on social accounts

---

## 📞 Support

1. Check logs: `logs/scraper.instagram.log`
2. Read docs: `docs/TROUBLESHOOTING.md`
3. Run in visible mode: `SCRAPER_HEADLESS=false`
4. Check test results: `pytest -v`

---

**Last Updated**: February 9, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
