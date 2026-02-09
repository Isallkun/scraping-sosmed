#!/usr/bin/env python3
"""
Simple script to verify project structure is set up correctly.
Does not require any external dependencies.
"""
import os
import sys
from pathlib import Path


def check_file(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} - NOT FOUND")
        return False


def check_directory(dirpath, description):
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print(f"✓ {description}: {dirpath}/")
        return True
    else:
        print(f"✗ {description}: {dirpath}/ - NOT FOUND")
        return False


def check_file_contains(filepath, text, description):
    """Check if a file contains specific text."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if text in content:
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} - NOT FOUND")
                return False
    except Exception as e:
        print(f"✗ {description} - ERROR: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("Social Media Scraper Automation - Project Structure Verification")
    print("=" * 70)
    print()
    
    all_passed = True
    
    # Check required files
    print("Checking required files...")
    print("-" * 70)
    all_passed &= check_file('requirements.txt', 'Python dependencies')
    all_passed &= check_file('requirements-dev.txt', 'Dev dependencies')
    all_passed &= check_file('.env.example', 'Environment template')
    all_passed &= check_file('.gitignore', 'Git ignore rules')
    all_passed &= check_file('README.md', 'Project documentation')
    all_passed &= check_file('SETUP.md', 'Setup guide')
    all_passed &= check_file('setup_venv.sh', 'Linux/Mac setup script')
    all_passed &= check_file('setup_venv.bat', 'Windows setup script')
    print()
    
    # Check required directories
    print("Checking required directories...")
    print("-" * 70)
    all_passed &= check_directory('scraper', 'Scraper module')
    all_passed &= check_directory('scraper/scrapers', 'Platform scrapers')
    all_passed &= check_directory('scraper/utils', 'Scraper utilities')
    all_passed &= check_directory('sentiment', 'Sentiment module')
    all_passed &= check_directory('sentiment/models', 'Sentiment models')
    all_passed &= check_directory('database', 'Database module')
    all_passed &= check_directory('database/migrations', 'DB migrations')
    all_passed &= check_directory('database/scripts', 'DB scripts')
    all_passed &= check_directory('n8n', 'n8n configuration')
    all_passed &= check_directory('n8n/workflows', 'n8n workflows')
    all_passed &= check_directory('scripts', 'Utility scripts')
    all_passed &= check_directory('tests', 'Test suite')
    all_passed &= check_directory('logs', 'Log directory')
    print()
    
    # Check Python package structure
    print("Checking Python package structure...")
    print("-" * 70)
    all_passed &= check_file('scraper/__init__.py', 'Scraper package init')
    all_passed &= check_file('scraper/scrapers/__init__.py', 'Scrapers package init')
    all_passed &= check_file('scraper/utils/__init__.py', 'Utils package init')
    all_passed &= check_file('sentiment/__init__.py', 'Sentiment package init')
    all_passed &= check_file('sentiment/models/__init__.py', 'Models package init')
    all_passed &= check_file('database/__init__.py', 'Database package init')
    print()
    
    # Check requirements.txt content
    print("Checking requirements.txt dependencies...")
    print("-" * 70)
    all_passed &= check_file_contains('requirements.txt', 'selenium', 'Selenium dependency')
    all_passed &= check_file_contains('requirements.txt', 'beautifulsoup4', 'BeautifulSoup dependency')
    all_passed &= check_file_contains('requirements.txt', 'pandas', 'Pandas dependency')
    all_passed &= check_file_contains('requirements.txt', 'vaderSentiment', 'VADER dependency')
    all_passed &= check_file_contains('requirements.txt', 'textblob', 'TextBlob dependency')
    all_passed &= check_file_contains('requirements.txt', 'psycopg2-binary', 'PostgreSQL dependency')
    all_passed &= check_file_contains('requirements.txt', 'python-dotenv', 'Dotenv dependency')
    print()
    
    # Check .env.example content
    print("Checking .env.example configuration...")
    print("-" * 70)
    all_passed &= check_file_contains('.env.example', 'SCRAPER_PLATFORM', 'Scraper platform config')
    all_passed &= check_file_contains('.env.example', 'SCRAPER_USERNAME', 'Scraper username config')
    all_passed &= check_file_contains('.env.example', 'SCRAPER_PASSWORD', 'Scraper password config')
    all_passed &= check_file_contains('.env.example', 'SCRAPER_RATE_LIMIT', 'Rate limit config')
    all_passed &= check_file_contains('.env.example', 'DATABASE_URL', 'Database URL config')
    all_passed &= check_file_contains('.env.example', 'SENTIMENT_MODEL', 'Sentiment model config')
    print()
    
    # Check .gitignore content
    print("Checking .gitignore patterns...")
    print("-" * 70)
    all_passed &= check_file_contains('.gitignore', '.env', 'Ignore .env file')
    all_passed &= check_file_contains('.gitignore', '__pycache__', 'Ignore Python cache')
    all_passed &= check_file_contains('.gitignore', 'venv/', 'Ignore virtual environment')
    all_passed &= check_file_contains('.gitignore', 'logs/', 'Ignore log files')
    print()
    
    # Summary
    print("=" * 70)
    if all_passed:
        print("✓ All checks passed! Project structure is set up correctly.")
        print()
        print("Next steps:")
        print("  1. Create virtual environment: python -m venv venv")
        print("  2. Activate it: source venv/bin/activate (Linux/Mac)")
        print("                  venv\\Scripts\\activate (Windows)")
        print("  3. Install dependencies: pip install -r requirements.txt")
        print("  4. Copy .env.example to .env and configure your settings")
        print("=" * 70)
        return 0
    else:
        print("✗ Some checks failed. Please review the output above.")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
