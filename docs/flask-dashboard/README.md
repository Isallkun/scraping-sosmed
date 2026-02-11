# Flask Analytics Dashboard

A lightweight, customizable web dashboard for visualizing Instagram scraping data stored in PostgreSQL. Built with Flask, Chart.js, and Tailwind CSS, this dashboard provides interactive visualizations, filtering capabilities, and a responsive user interface.

## Features

- **📊 Interactive Visualizations**: Charts and graphs powered by Chart.js
- **🔍 Data Explorer**: Search, filter, and export post data
- **📈 Sentiment Analysis**: Visualize sentiment trends and distribution
- **💬 Engagement Metrics**: Track likes, comments, and engagement rates
- **📝 Content Analysis**: Analyze hashtags, posting patterns, and content length
- **🌓 Dark Mode**: Toggle between light and dark themes
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ Performance Optimized**: Caching, gzip compression, and lazy loading
- **🔄 Auto-refresh**: Optional automatic data updates

## Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd scraping-sosmed
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure your database connection:
   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=social_scraper
   DB_USER=postgres
   DB_PASSWORD=your_password
   
   # Flask Configuration
   FLASK_ENV=development
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   
   # Cache Configuration
   CACHE_TYPE=simple
   CACHE_DEFAULT_TIMEOUT=300
   
   # Dashboard Configuration
   AUTO_REFRESH_INTERVAL=30
   ```

4. **Initialize the database**:
   
   Run the database migration script:
   ```bash
   python database/scripts/run_migrations.py
   ```

5. **Import sample data** (optional):
   
   Import Instagram data from JSON or CSV files:
   ```bash
   python scripts/import_data.py --input output/instagram/raw/ --type json
   ```

6. **Run the Flask application**:
   ```bash
   python run_flask.py
   ```

7. **Access the dashboard**:
   
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Documentation

- [Installation Guide](INSTALLATION.md) - Detailed installation instructions
- [Usage Guide](USAGE.md) - How to use the dashboard features
- [API Documentation](API.md) - RESTful API endpoints reference
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## Project Structure

```
scraping-sosmed/
├── app/                        # Flask application
│   ├── __init__.py            # App factory and configuration
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database initialization
│   ├── routes/                # Route blueprints
│   │   ├── api.py            # API endpoints
│   │   └── pages.py          # HTML page routes
│   └── services/              # Business logic
│       ├── data_service.py   # Data queries and transformations
│       └── utils.py          # Utility functions
├── templates/                  # Jinja2 HTML templates
│   ├── base.html             # Base template
│   ├── home.html             # Overview page
│   ├── sentiment.html        # Sentiment analysis page
│   ├── engagement.html       # Engagement metrics page
│   ├── content.html          # Content analysis page
│   ├── explorer.html         # Data explorer page
│   └── error.html            # Error page
├── static/                     # Static assets
│   ├── css/                  # Stylesheets
│   │   └── style.css
│   └── js/                   # JavaScript files
│       ├── common.js         # Shared utilities
│       ├── home.js           # Home page charts
│       ├── sentiment.js      # Sentiment page charts
│       ├── engagement.js     # Engagement page charts
│       ├── content.js        # Content page charts
│       └── explorer.js       # Data explorer logic
├── database/                   # Database module
│   ├── db_connection.py      # Connection management
│   ├── db_operations.py      # CRUD operations
│   └── migrations/           # SQL migration scripts
├── scripts/                    # Utility scripts
│   └── import_data.py        # Data import script
├── docs/                       # Documentation
│   └── flask-dashboard/      # Dashboard documentation
├── logs/                       # Application logs
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not in git)
└── run_flask.py              # Application entry point
```

## Key Technologies

- **Backend**: Flask 3.0, Python 3.8+
- **Database**: PostgreSQL 12+, psycopg2
- **Frontend**: Tailwind CSS, Chart.js 4.4
- **Caching**: Flask-Caching
- **Compression**: Flask-Compress

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `social_scraper` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | - | Database password |
| `DEBUG` | `False` | Enable debug mode |
| `CACHE_TYPE` | `simple` | Cache backend (simple, redis) |
| `CACHE_DEFAULT_TIMEOUT` | `300` | Cache timeout in seconds |
| `AUTO_REFRESH_INTERVAL` | `30` | Auto-refresh interval in seconds |

### Cache Configuration

For production, use Redis for caching:

```env
CACHE_TYPE=redis
CACHE_REDIS_HOST=localhost
CACHE_REDIS_PORT=6379
CACHE_REDIS_DB=0
```

## Development

### Running in Development Mode

```bash
# Enable debug mode
export DEBUG=True

# Run with auto-reload
python run_flask.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Using Docker

```bash
# Build Docker image
docker build -t flask-dashboard .

# Run container
docker run -p 5000:5000 --env-file .env flask-dashboard
```

## Performance Optimization

The dashboard includes several performance optimizations:

- **Query Result Caching**: API responses are cached for 5 minutes
- **Gzip Compression**: HTTP responses are compressed
- **Async Script Loading**: JavaScript libraries load asynchronously
- **Lazy Loading**: Data explorer loads data on demand
- **Database Indexes**: Optimized queries with proper indexes
- **Connection Pooling**: Efficient database connection management

## Security Considerations

- **Parameterized Queries**: All database queries use parameterized statements to prevent SQL injection
- **Environment Variables**: Sensitive configuration stored in `.env` file (not in git)
- **Error Handling**: Production mode hides error details from users
- **CORS**: Cross-Origin Resource Sharing configured for API endpoints

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new features
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or feature requests:

- Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
- Review the [API Documentation](API.md)
- Check application logs in `logs/flask_dashboard.log`

## Changelog

See [CHANGELOG.md](../../docs/CHANGELOG.md) for version history and updates.
