# Installation Guide

This guide provides detailed instructions for installing and setting up the Flask Analytics Dashboard.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **RAM**: 2 GB minimum, 4 GB recommended
- **Disk Space**: 500 MB for application and dependencies

### Recommended Requirements

- **Python**: 3.10 or higher
- **PostgreSQL**: 14 or higher
- **RAM**: 8 GB or more
- **Disk Space**: 2 GB or more (for data storage)

## Installation Steps

### Step 1: Install Python

#### Windows

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```bash
   python --version
   ```

#### macOS

Using Homebrew:
```bash
brew install python@3.10
```

Or download from [python.org](https://www.python.org/downloads/)

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.10 python3-pip python3-venv
```

### Step 2: Install PostgreSQL

#### Windows

1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run the installer
3. Remember the password you set for the `postgres` user
4. Default port is 5432

#### macOS

Using Homebrew:
```bash
brew install postgresql@14
brew services start postgresql@14
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 3: Clone the Repository

```bash
git clone <repository-url>
cd scraping-sosmed
```

### Step 4: Create Virtual Environment (Recommended)

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask 3.0.0
- Flask-Caching 2.1.0
- Flask-CORS 4.0.0
- Flask-Compress 1.14
- psycopg2-binary 2.9.9
- python-dotenv 1.0.0
- And other dependencies

### Step 6: Verify Installation

```bash
python -c "import flask; print(f'Flask version: {flask.__version__}')"
python -c "import psycopg2; print('psycopg2 installed successfully')"
```

## Database Setup

### Step 1: Create Database

#### Using psql (Command Line)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE social_scraper;

# Create user (optional)
CREATE USER dashboard_user WITH PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE social_scraper TO dashboard_user;

# Exit psql
\q
```

#### Using pgAdmin (GUI)

1. Open pgAdmin
2. Right-click on "Databases"
3. Select "Create" > "Database"
4. Enter database name: `social_scraper`
5. Click "Save"

### Step 2: Run Database Migrations

```bash
python database/scripts/run_migrations.py
```

This will create the following tables:
- `posts` - Instagram post data
- `sentiments` - Sentiment analysis results
- `execution_logs` - Workflow execution logs

### Step 3: Verify Database Schema

```bash
# Connect to database
psql -U postgres -d social_scraper

# List tables
\dt

# View posts table structure
\d posts

# Exit
\q
```

Expected tables:
- posts
- sentiments
- execution_logs

## Configuration

### Step 1: Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Edit Configuration

Open `.env` in a text editor and configure:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social_scraper
DB_USER=postgres
DB_PASSWORD=your_password_here

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

### Step 3: Generate Secret Key

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as the `SECRET_KEY` value in `.env`.

### Configuration Options Explained

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_HOST` | PostgreSQL server hostname | `localhost` | Yes |
| `DB_PORT` | PostgreSQL server port | `5432` | Yes |
| `DB_NAME` | Database name | `social_scraper` | Yes |
| `DB_USER` | Database username | `postgres` | Yes |
| `DB_PASSWORD` | Database password | - | Yes |
| `DEBUG` | Enable debug mode | `False` | No |
| `SECRET_KEY` | Flask secret key for sessions | - | Yes |
| `CACHE_TYPE` | Cache backend type | `simple` | No |
| `CACHE_DEFAULT_TIMEOUT` | Cache timeout in seconds | `300` | No |
| `AUTO_REFRESH_INTERVAL` | Auto-refresh interval in seconds | `30` | No |

## Verification

### Step 1: Test Database Connection

```bash
python -c "from database.db_connection import get_db_connection; db = get_db_connection(); print('Database connection successful')"
```

### Step 2: Run Flask Application

```bash
python run_flask.py
```

Expected output:
```
[2024-02-10 15:00:00] INFO Flask Analytics Dashboard starting...
[2024-02-10 15:00:00] INFO Debug mode: True
[2024-02-10 15:00:00] INFO Database: social_scraper at localhost:5432
[2024-02-10 15:00:00] INFO Database connection established successfully
 * Running on http://127.0.0.1:5000
```

### Step 3: Access Dashboard

Open your web browser and navigate to:
```
http://localhost:5000
```

You should see the dashboard home page.

### Step 4: Test API Endpoints

Test the API endpoints:

```bash
# Test summary endpoint
curl http://localhost:5000/api/summary

# Test sentiment endpoint
curl http://localhost:5000/api/sentiment

# Test posts endpoint
curl http://localhost:5000/api/posts?page=1&per_page=10
```

## Import Sample Data

To populate the dashboard with data:

### Import JSON Files

```bash
python scripts/import_data.py --input output/instagram/raw/ --type json
```

### Import CSV Files

```bash
python scripts/import_data.py --input output/instagram/sentiment/ --type csv
```

### Import Single File

```bash
python scripts/import_data.py --file output/instagram/raw/posts_20260209.json
```

## Troubleshooting

### Database Connection Errors

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
1. Verify PostgreSQL is running:
   ```bash
   # Windows
   sc query postgresql-x64-14
   
   # macOS
   brew services list
   
   # Linux
   sudo systemctl status postgresql
   ```

2. Check database credentials in `.env`
3. Verify PostgreSQL is listening on the correct port:
   ```bash
   psql -U postgres -c "SHOW port;"
   ```

### Module Import Errors

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solutions**:
1. Stop the process using port 5000:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   
   # macOS/Linux
   lsof -ti:5000 | xargs kill -9
   ```

2. Or run Flask on a different port:
   ```bash
   export FLASK_RUN_PORT=5001
   python run_flask.py
   ```

### Permission Errors

**Error**: `PermissionError: [Errno 13] Permission denied`

**Solutions**:
1. Run with appropriate permissions
2. Check file ownership:
   ```bash
   ls -la logs/
   ```
3. Create logs directory if missing:
   ```bash
   mkdir -p logs
   ```

### Database Migration Errors

**Error**: `relation "posts" already exists`

**Solution**: The tables already exist. Skip migration or drop and recreate:
```bash
# Drop existing tables (WARNING: This deletes all data)
psql -U postgres -d social_scraper -c "DROP TABLE IF EXISTS sentiments, posts, execution_logs CASCADE;"

# Run migration again
python database/scripts/run_migrations.py
```

## Next Steps

After successful installation:

1. Read the [Usage Guide](USAGE.md) to learn how to use the dashboard
2. Review the [API Documentation](API.md) for API endpoint details
3. Import your Instagram data using the import script
4. Explore the dashboard features

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review application logs in `logs/flask_dashboard.log`
3. Check database logs
4. Verify all environment variables are set correctly
