# Setup Guide

This guide will help you set up the Social Media Scraper Automation project.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**: [Download Python](https://www.python.org/downloads/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **Docker & Docker Compose** (optional, for containerized deployment): [Download Docker](https://www.docker.com/get-started)

## Setup Methods

You can set up the project in two ways:

### Method 1: Local Python Environment (Development)

This method is recommended for development and testing.

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd social-media-scraper-automation
```

#### Step 2: Create Virtual Environment

**On Linux/macOS:**
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

**On Windows:**
```cmd
setup_venv.bat
```

**Or manually:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
# Use your favorite text editor (nano, vim, VSCode, etc.)
nano .env
```

**Required Configuration:**
- `SCRAPER_USERNAME`: Your social media account username
- `SCRAPER_PASSWORD`: Your social media account password
- `DATABASE_URL`: PostgreSQL connection string
- Notification settings (SMTP, Slack, or Telegram)

#### Step 4: Set Up Database

**Option A: Use Docker for PostgreSQL only**
```bash
docker run -d \
  --name postgres-scraper \
  -e POSTGRES_USER=scraper_user \
  -e POSTGRES_PASSWORD=scraper_password \
  -e POSTGRES_DB=social_scraper \
  -p 5432:5432 \
  postgres:14
```

**Option B: Use local PostgreSQL**
```bash
# Install PostgreSQL on your system
# Then create database and user:
psql -U postgres
CREATE DATABASE social_scraper;
CREATE USER scraper_user WITH PASSWORD 'scraper_password';
GRANT ALL PRIVILEGES ON DATABASE social_scraper TO scraper_user;
\q
```

#### Step 5: Run Database Migrations

```bash
# This will be implemented in later tasks
# For now, the database schema will be created automatically
```

#### Step 6: Test the Setup

```bash
# Test scraper (will be implemented in later tasks)
python scraper/main_scraper.py --help

# Test sentiment analyzer (will be implemented in later tasks)
python sentiment/sentiment_analyzer.py --help
```

### Method 2: Docker Deployment (Production)

This method is recommended for production deployment.

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd social-media-scraper-automation
```

#### Step 2: Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your settings
```

#### Step 3: Start Services with Docker Compose

```bash
# Start all services (n8n, PostgreSQL, scraper)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Step 4: Access n8n

Open your browser and navigate to:
```
http://localhost:5678
```

Default credentials (change these in .env):
- Username: admin
- Password: change_this_password

#### Step 5: Import Workflows

1. Log in to n8n
2. Click "Workflows" in the sidebar
3. Click "Import from File"
4. Import workflows from `n8n/workflows/` directory

## Verification

### Check Python Environment

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Check Python version
python --version

# Check installed packages
pip list
```

### Check Docker Services

```bash
# Check running containers
docker-compose ps

# Check service health
docker-compose exec postgres pg_isready

# Check n8n
curl http://localhost:5678/healthz
```

### Check Database Connection

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U scraper_user -d social_scraper

# Or from local machine
psql -h localhost -U scraper_user -d social_scraper
```

## Directory Structure

After setup, your project should look like this:

```
social-media-scraper-automation/
├── venv/                      # Python virtual environment (local setup)
├── scraper/                   # Scraper module
├── sentiment/                 # Sentiment analysis module
├── database/                  # Database module
├── n8n/                      # n8n workflows
├── scripts/                  # Utility scripts
├── tests/                    # Test suite
├── logs/                     # Application logs
├── .env                      # Your configuration (not in git)
├── .env.example             # Configuration template
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker configuration
└── README.md               # Project documentation
```

## Next Steps

1. **Configure Credentials**: Update `.env` with your social media credentials
2. **Test Scraper**: Run a test scrape to verify setup
3. **Set Up Workflows**: Import and configure n8n workflows
4. **Schedule Jobs**: Configure cron schedules for automated scraping
5. **Monitor Logs**: Check logs for any errors or issues

## Troubleshooting

### Virtual Environment Issues

**Problem**: `python: command not found`
- **Solution**: Install Python 3.11+ from python.org

**Problem**: `pip: command not found`
- **Solution**: Ensure pip is installed: `python -m ensurepip --upgrade`

### Docker Issues

**Problem**: `docker: command not found`
- **Solution**: Install Docker Desktop from docker.com

**Problem**: Port already in use (5432, 5678)
- **Solution**: Stop conflicting services or change ports in docker-compose.yml

### Database Issues

**Problem**: Connection refused to PostgreSQL
- **Solution**: Ensure PostgreSQL is running and credentials are correct

**Problem**: Permission denied
- **Solution**: Grant proper permissions to database user

### Selenium Issues

**Problem**: ChromeDriver version mismatch
- **Solution**: Update Chrome browser or install matching ChromeDriver

**Problem**: Browser not found in headless mode
- **Solution**: Install Chrome/Chromium or set `SCRAPER_HEADLESS=false`

## Getting Help

- Check the [README.md](README.md) for general information
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [SECURITY.md](SECURITY.md) for security best practices
- Open an issue on GitHub for bugs or questions

## Security Reminders

- ⚠️ Never commit `.env` file to version control
- ⚠️ Use strong passwords for database and n8n
- ⚠️ Keep credentials secure and rotate them regularly
- ⚠️ Use rate limiting to respect platform terms of service
- ⚠️ Review and comply with data privacy regulations
