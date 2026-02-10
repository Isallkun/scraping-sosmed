# Flask Analytics Dashboard

A lightweight web dashboard for visualizing Instagram scraping results stored in PostgreSQL.

## Features

- **Interactive Visualizations**: Charts and graphs powered by Chart.js
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **RESTful API**: JSON endpoints for programmatic access
- **Real-time Updates**: Auto-refresh functionality for live data
- **Data Explorer**: Search, filter, and export post data
- **Sentiment Analysis**: Visualize emotional tone of content
- **Engagement Metrics**: Track likes, comments, and engagement rates
- **Content Analysis**: Hashtag trends and posting patterns

## Project Structure

```
app/
├── __init__.py           # Flask app factory and initialization
├── config.py             # Configuration management
├── routes/               # Route blueprints
│   ├── __init__.py
│   ├── pages.py         # HTML page routes
│   └── api.py           # API endpoint routes
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── data_service.py  # Data query and transformation
│   └── utils.py         # Utility functions
└── database.py          # Database connection wrapper

templates/               # Jinja2 HTML templates
├── base.html           # Base template with navigation
├── home.html           # Overview dashboard
├── sentiment.html      # Sentiment analysis page
├── engagement.html     # Engagement metrics page
├── content.html        # Content analysis page
└── explorer.html       # Data explorer page

static/                 # Static assets
├── css/
│   └── style.css       # Custom styles
└── js/
    ├── common.js       # Shared utilities
    ├── home.js         # Home page charts
    ├── sentiment.js    # Sentiment page charts
    ├── engagement.js   # Engagement page charts
    ├── content.js      # Content page charts
    └── explorer.js     # Data explorer logic

scripts/                # Utility scripts
└── import_data.py      # Data import script
```

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database (with schema from `database/migrations/001_initial_schema.sql`)
- pip package manager

### Setup Steps

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Configure Environment Variables**

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database connection
- `FLASK_PORT` - Server port (default: 5000)
- `SECRET_KEY` - Flask secret key (generate a random string)
- `DEBUG` - Set to `true` for development, `false` for production
- `CACHE_TYPE` - Use `simple` for development, `redis` for production

3. **Initialize Database**

Ensure the PostgreSQL database is created and the schema is applied:

```bash
psql -U postgres -d instagram_analytics -f database/migrations/001_initial_schema.sql
```

4. **Run the Application**

```bash
python run_flask.py
```

The dashboard will be available at `http://localhost:5000`

## Usage

### Accessing the Dashboard

Open your web browser and navigate to:
- **Home**: `http://localhost:5000/` - Overview statistics
- **Sentiment**: `http://localhost:5000/sentiment` - Sentiment analysis
- **Engagement**: `http://localhost:5000/engagement` - Engagement metrics
- **Content**: `http://localhost:5000/content` - Content analysis
- **Explorer**: `http://localhost:5000/explorer` - Data explorer

### Importing Data

Use the import script to load Instagram data into the database:

```bash
# Import a single JSON file
python scripts/import_data.py --file output/instagram/raw/posts_20260209.json

# Import all JSON files from a directory
python scripts/import_data.py --input output/instagram/raw/ --type json

# Import CSV files with sentiment data
python scripts/import_data.py --input output/instagram/sentiment/ --type csv --batch
```

### API Endpoints

The dashboard provides RESTful API endpoints for programmatic access:

- `GET /api/summary` - Overall statistics
- `GET /api/sentiment?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Sentiment data
- `GET /api/engagement?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Engagement metrics
- `GET /api/content?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Content analysis
- `GET /api/posts?page=1&per_page=25&search=term&filter=value` - Paginated posts
- `GET /api/export?filters=...` - CSV export

Example API request:

```bash
curl http://localhost:5000/api/summary
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_HOST` | Server host address | `0.0.0.0` |
| `FLASK_PORT` | Server port | `5000` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key-change-in-production` |
| `DEBUG` | Debug mode (true/false) | `false` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `instagram_analytics` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `` |
| `CACHE_TYPE` | Cache backend (simple/redis) | `simple` |
| `CACHE_TIMEOUT` | Cache timeout in seconds | `300` |
| `CACHE_REDIS_URL` | Redis URL for caching | `redis://localhost:6379/0` |
| `AUTO_REFRESH_INTERVAL` | Auto-refresh interval in seconds | `30` |
| `POSTS_PER_PAGE` | Posts per page in explorer | `25` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

### Logging

Logs are written to:
- **Console**: Standard output with colored formatting
- **File**: `logs/flask_dashboard.log` (rotates at 10 MB, keeps 5 backups)

Log levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors that prevent operation

## Development

### Running in Debug Mode

Set `DEBUG=true` in `.env` to enable:
- Auto-reload on code changes
- Detailed error pages
- SQL query logging
- Verbose console output

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_routes_api.py
```

### Code Style

Follow PEP 8 style guidelines. Use tools like:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

## Production Deployment

For production deployment, use a WSGI server instead of the Flask development server:

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run_flask:app
```

### Using uWSGI

```bash
pip install uwsgi
uwsgi --http 0.0.0.0:5000 --wsgi-file run_flask.py --callable app --processes 4
```

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Use Redis for caching (`CACHE_TYPE=redis`)
- [ ] Configure proper database credentials
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Enable monitoring and alerting
- [ ] Configure backup strategy

## Troubleshooting

### Database Connection Errors

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**: 
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists and schema is applied
- Check firewall rules allow connection to PostgreSQL port

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**: Install dependencies with `pip install -r requirements.txt`

### Port Already in Use

**Error**: `OSError: [Errno 98] Address already in use`

**Solution**: 
- Change `FLASK_PORT` in `.env` to a different port
- Or stop the process using port 5000: `lsof -ti:5000 | xargs kill -9`

### Cache Errors

**Error**: `ConnectionError: Error connecting to Redis`

**Solution**: 
- If using Redis, ensure Redis server is running
- Or switch to simple cache: `CACHE_TYPE=simple` in `.env`

### Empty Dashboard

**Issue**: Dashboard shows no data

**Solution**:
- Import data using `scripts/import_data.py`
- Verify data exists in database: `psql -U postgres -d instagram_analytics -c "SELECT COUNT(*) FROM posts;"`
- Check browser console for JavaScript errors

## License

This project is part of the Instagram Analytics system.

## Support

For issues and questions, please refer to the main project documentation.
