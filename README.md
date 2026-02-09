# Social Media Scraper Automation

An automated system for scraping social media data, performing sentiment analysis, and generating reports using n8n workflow orchestration.

## Features

- 🔍 **Web Scraping**: Automated data collection from Instagram, Twitter, and Facebook using Selenium
- 🎭 **Anti-Detection**: Random user agents, viewport sizes, and human-like delays to avoid bot detection
- 📊 **Sentiment Analysis**: Analyze text sentiment using VADER and TextBlob models
- 🗄️ **Data Storage**: PostgreSQL database for structured data storage with automatic backups
- 🔄 **Workflow Automation**: n8n workflows for scheduled scraping, on-demand analysis, and weekly reporting
- 📧 **Notifications**: Email, Slack, and Telegram alerts for workflow status and errors
- 🐳 **Docker Deployment**: Containerized deployment for easy setup and scalability

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        n8n Workflows                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Daily Cron   │  │  On-Demand   │  │   Weekly     │      │
│  │   Workflow   │  │   Webhook    │  │   Report     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python Services Layer                     │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │  Selenium Scraper    │───▶│  Sentiment Analyzer  │      │
│  │  - Login automation  │    │  - Text cleaning     │      │
│  │  - Data extraction   │    │  - VADER/TextBlob    │      │
│  │  - Anti-detection    │    │  - Batch processing  │      │
│  │  - Rate limiting     │    │  - Score calculation │      │
│  └──────────┬───────────┘    └──────────┬───────────┘      │
└─────────────┼──────────────────────────┼─────────────────────┘
              │                          │
              ▼                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐          │
│  │  posts   │  │sentiments│  │ execution_logs   │          │
│  └──────────┘  └──────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
.
├── scraper/                    # Web scraping module
│   ├── __init__.py
│   ├── main_scraper.py        # CLI entry point
│   ├── config.py              # Configuration management
│   ├── scrapers/              # Platform-specific scrapers
│   │   ├── __init__.py
│   │   ├── base_scraper.py   # Abstract base class
│   │   ├── instagram.py      # Instagram scraper
│   │   ├── twitter.py        # Twitter scraper
│   │   └── facebook.py       # Facebook scraper
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── anti_detection.py # Anti-detection measures
│       ├── rate_limiter.py   # Rate limiting
│       └── logger.py         # Logging configuration
│
├── sentiment/                  # Sentiment analysis module
│   ├── __init__.py
│   ├── sentiment_analyzer.py # Main analyzer
│   ├── text_cleaner.py       # Text preprocessing
│   ├── config.py             # Configuration
│   └── models/               # Sentiment models
│       ├── __init__.py
│       ├── vader_model.py    # VADER implementation
│       └── textblob_model.py # TextBlob implementation
│
├── database/                   # Database module
│   ├── __init__.py
│   ├── db_connection.py      # Connection pooling
│   ├── db_operations.py      # CRUD operations
│   ├── migrations/           # SQL migration scripts
│   └── scripts/              # Backup and maintenance scripts
│
├── n8n/                       # n8n workflow configurations
│   ├── workflows/            # Workflow JSON exports
│   └── .env.n8n.example     # n8n environment variables
│
├── scripts/                   # Utility scripts
│   ├── setup.sh             # Docker setup script
│   ├── health_check.py      # Health monitoring
│   └── notify.py            # Notification utilities
│
├── tests/                     # Test suite
│   ├── unit/                # Unit tests
│   ├── property/            # Property-based tests
│   └── integration/         # Integration tests
│
├── logs/                      # Application logs
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile               # Python service Dockerfile
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🚀 Quick Start

### ⚡ Fastest Way (3 Commands)

```bash
# 1. Generate demo data (no login required)
python demo_scraper.py

# 2. Analyze sentiment
python -m sentiment.main_analyzer --input output/demo_instagram_posts_TIMESTAMP.json --output output/demo_instagram_posts_TIMESTAMP_sentiment.json

# 3. View beautiful results
python view_results.py output/demo_instagram_posts_TIMESTAMP_sentiment.json
```

**See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for more commands!**

---

### Prerequisites

- Python 3.11+
- Chrome/Chromium browser (for real scraping)
- Instagram account (for real scraping)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd social-media-scraper-automation
   ```

2. **Set up Python virtual environment**
   ```bash
   # Windows
   setup_venv.bat
   
   # Linux/Mac
   chmod +x setup_venv.sh
   ./setup_venv.sh
   ```

3. **Configure credentials (for real scraping)**
   ```bash
   # Edit .env file with your Instagram credentials
   INSTAGRAM_USERNAME=your_username
   INSTAGRAM_PASSWORD=your_password
   ```

### Usage

#### 📸 Real Instagram Scraping (Simplified & Fast)

```bash
# Scrape 5 posts from a profile (includes both posts and reels)
python scrape_instagram_simple.py https://www.instagram.com/rusdi_sutejo/ 5

# Analyze sentiment
python -m sentiment.main_analyzer --input output/instagram_simple_TIMESTAMP.json --output output/instagram_simple_TIMESTAMP_sentiment.json

# View results
python view_results.py output/instagram_simple_TIMESTAMP_sentiment.json
```

**Status**: ✅ **WORKING** - Tested February 9, 2026  
**Features**:
- ✅ Scrapes both regular posts (`/p/`) and reels (`/reel/`)
- ✅ Enhanced comment extraction with 3-strategy fallback
- ✅ Extracts comment text, author, and timestamp
- ✅ Supports Indonesian and English UI

**See**: [docs/INSTAGRAM_SIMPLIFIED_GUIDE.md](docs/INSTAGRAM_SIMPLIFIED_GUIDE.md) for complete guide

#### 🎭 Demo Mode (Safe Testing)

```bash
# Generate demo data
python demo_scraper.py

# Analyze demo data
python -m sentiment.main_analyzer --input output/demo_instagram_posts_TIMESTAMP.json --output output/demo_instagram_posts_TIMESTAMP_sentiment.json

# View demo results
python view_results.py output/demo_instagram_posts_TIMESTAMP_sentiment.json
```

**Status**: ✅ **100% WORKING** - No credentials needed

#### 🔄 Batch Scripts (Windows)

```bash
# Quick scraping
run_scraper.bat

# Quick sentiment analysis
run_sentiment.bat output/instagram_simple_TIMESTAMP.json
```

## Configuration

All configuration is managed through environment variables. See `.env.example` for a complete list of available options.

### Key Configuration Options

- `SCRAPER_PLATFORM`: Target platform (instagram, twitter, facebook)
- `SCRAPER_RATE_LIMIT`: Requests per minute (default: 30)
- `SENTIMENT_MODEL`: Sentiment model (vader, textblob)
- `DATABASE_URL`: PostgreSQL connection string
- `SMTP_*`: Email notification settings
- `SLACK_WEBHOOK_URL`: Slack notification webhook

## 📋 Output Schema

### Enhanced Instagram Post Object

The scraper now extracts both posts and reels with enhanced comment data:

```json
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
}
```

### New Fields

- **`post_type`**: Identifies content as `"post"` or `"reel"` based on URL pattern
- **`comments`**: Array of comment objects with:
  - `author`: Username of commenter
  - `text`: Comment text content
  - `timestamp`: ISO 8601 timestamp (when available)

### Enhanced Metadata

```json
{
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
}
```

### Comment Extraction Strategies

The scraper uses a 3-strategy fallback approach for robust comment extraction:

1. **Strategy 1: Page Source JSON** - Parses embedded JSON from `window._sharedData` or `__additionalDataLoaded`
2. **Strategy 2: DOM Extraction** - Uses WebDriverWait and DOM selectors to extract comments with:
   - Automatic "View all comments" button clicking
   - Scroll and "Load more" support (up to 5 iterations)
   - Filters out captions and UI text
3. **Strategy 3: JavaScript Fallback** - Direct DOM query via `execute_script()` for elements Selenium might miss

Each strategy is tried in order until comments are successfully extracted. If all strategies fail, an empty array is returned (graceful degradation).

## Security & Compliance

⚠️ **Important Disclaimers**:

- This tool is for educational and research purposes
- Always respect platform Terms of Service and robots.txt
- Use rate limiting to avoid overwhelming servers
- Never share or expose credentials
- Comply with data privacy regulations (GDPR, CCPA, etc.)

### Security Best Practices

- Store credentials in environment variables, never in code
- Use rate limiting to respect platform limits
- Run containers as non-root users
- Regularly update dependencies for security patches
- Enable log sanitization to prevent credential leaks

## ✅ Current Status

### Working Features
- ✅ **Demo Mode** - 100% working, generates sample data
- ✅ **Instagram Scraping** - Simplified fast scraper working (tested Feb 9, 2026)
- ✅ **Sentiment Analysis** - VADER and TextBlob models working
- ✅ **Results Viewer** - Beautiful formatted output
- ✅ **Database Integration** - PostgreSQL storage working
- ✅ **Testing Suite** - 305 tests passing (100% pass rate)

### In Development
- 🔄 Twitter scraping (basic implementation done)
- 🔄 Facebook scraping (basic implementation done)
- 🔄 n8n workflow automation
- 🔄 Full Instagram data extraction (UI changes make this challenging)

### Known Limitations
- ⚠️ Instagram simplified scraper extracts minimal data (post IDs and URLs)
- ⚠️ Full caption/likes/comments extraction affected by Instagram UI changes
- ⚠️ Twitter and Facebook scrapers need real-world testing

**See [docs/REAL_SCRAPING_COMPLETION.md](docs/REAL_SCRAPING_COMPLETION.md) for detailed status**

---

## Testing

```bash
# Run all tests (305 tests)
pytest

# Run specific test file
pytest tests/test_instagram_scraper.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=scraper --cov=sentiment
```

**Test Status**: ✅ 305 tests passing, 0 failures

---

## 📚 Documentation

### Quick Guides
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - ⚡ Quick command reference
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - 🚀 Quick start guide
- **[docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)** - 📖 Complete usage guide

### Instagram Scraping
- **[docs/INSTAGRAM_SIMPLIFIED_GUIDE.md](docs/INSTAGRAM_SIMPLIFIED_GUIDE.md)** - 📸 Simplified scraping guide
- **[docs/REAL_SCRAPING_GUIDE.md](docs/REAL_SCRAPING_GUIDE.md)** - ⚠️ Real scraping warnings
- **[docs/REAL_SCRAPING_COMPLETION.md](docs/REAL_SCRAPING_COMPLETION.md)** - ✅ Completion summary

### Troubleshooting
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - 🔧 Common issues and solutions

### Database & Setup
- **[database/README.md](database/README.md)** - 🗄️ Database setup guide
- **[docs/SETUP.md](docs/SETUP.md)** - ⚙️ Detailed setup instructions

## Troubleshooting

### Common Issues

**Selenium WebDriver errors**:
- Ensure Chrome/Chromium is installed
- Check ChromeDriver version matches Chrome version
- Try running in non-headless mode for debugging

**Database connection errors**:
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists and user has permissions

**Rate limiting / IP blocking**:
- Increase delay between requests
- Use residential proxies
- Reduce SCRAPER_RATE_LIMIT value

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Selenium](https://www.selenium.dev/) - Web browser automation
- [VADER Sentiment](https://github.com/cjhutto/vaderSentiment) - Social media sentiment analysis
- [n8n](https://n8n.io/) - Workflow automation platform
- [PostgreSQL](https://www.postgresql.org/) - Database system

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Disclaimer**: This tool is provided as-is for educational purposes. Users are responsible for ensuring their use complies with applicable laws, regulations, and platform terms of service.
