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

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 14+ (or use Docker)
- Chrome/Chromium browser (for Selenium)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd social-media-scraper-automation
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials and configuration
   ```

4. **Run with Docker (Recommended)**
   ```bash
   docker-compose up -d
   ```

   Or use the setup script:
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

### Usage

#### CLI Scraping

```bash
# Scrape Instagram posts
python scraper/main_scraper.py \
  --platform instagram \
  --target "https://instagram.com/username" \
  --limit 50 \
  --output posts.json

# Analyze sentiment
python sentiment/sentiment_analyzer.py \
  --input posts.json \
  --output posts_with_sentiment.json \
  --model vader
```

#### n8n Workflows

Access n8n at `http://localhost:5678` and import workflows from `n8n/workflows/`:

- **Daily Scraping**: Automated daily data collection (runs at 2 AM)
- **On-Demand Webhook**: Trigger scraping via HTTP POST to `/webhook/scrape`
- **Weekly Report**: Generate and email weekly insights (runs Sunday 9 AM)

## Configuration

All configuration is managed through environment variables. See `.env.example` for a complete list of available options.

### Key Configuration Options

- `SCRAPER_PLATFORM`: Target platform (instagram, twitter, facebook)
- `SCRAPER_RATE_LIMIT`: Requests per minute (default: 30)
- `SENTIMENT_MODEL`: Sentiment model (vader, textblob)
- `DATABASE_URL`: PostgreSQL connection string
- `SMTP_*`: Email notification settings
- `SLACK_WEBHOOK_URL`: Slack notification webhook

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

## Testing

```bash
# Run unit tests
pytest tests/unit/

# Run property-based tests
pytest tests/property/

# Run integration tests
pytest tests/integration/

# Run all tests with coverage
pytest --cov=. --cov-report=html
```

## Documentation

- [Architecture Details](ARCHITECTURE.md) - System design and component interactions
- [API Documentation](API.md) - Webhook endpoints and request/response formats
- [Security Guide](SECURITY.md) - Security best practices and compliance
- [Deployment Guide](DEPLOYMENT.md) - Docker deployment instructions
- [Database Restore](database/RESTORE.md) - Backup and restore procedures

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
