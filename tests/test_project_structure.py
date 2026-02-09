"""
Test to verify project structure is set up correctly.
"""
import os
import sys
from pathlib import Path


def test_project_root_exists():
    """Test that we're in the project root directory."""
    assert Path('.').exists()


def test_required_files_exist():
    """Test that all required configuration files exist."""
    required_files = [
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'README.md',
        'SETUP.md',
        'setup_venv.sh',
        'setup_venv.bat',
    ]
    
    for file in required_files:
        assert Path(file).exists(), f"Required file {file} does not exist"


def test_required_directories_exist():
    """Test that all required directories exist."""
    required_dirs = [
        'scraper',
        'scraper/scrapers',
        'scraper/utils',
        'sentiment',
        'sentiment/models',
        'database',
        'database/migrations',
        'database/scripts',
        'n8n',
        'n8n/workflows',
        'scripts',
        'tests',
        'logs',
    ]
    
    for directory in required_dirs:
        assert Path(directory).is_dir(), f"Required directory {directory} does not exist"


def test_python_packages_have_init():
    """Test that Python packages have __init__.py files."""
    packages = [
        'scraper',
        'scraper/scrapers',
        'scraper/utils',
        'sentiment',
        'sentiment/models',
        'database',
    ]
    
    for package in packages:
        init_file = Path(package) / '__init__.py'
        assert init_file.exists(), f"Package {package} missing __init__.py"


def test_requirements_txt_has_dependencies():
    """Test that requirements.txt contains expected dependencies."""
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    required_deps = [
        'selenium',
        'beautifulsoup4',
        'pandas',
        'vaderSentiment',
        'textblob',
        'psycopg2-binary',
        'python-dotenv',
    ]
    
    for dep in required_deps:
        assert dep in content, f"Required dependency {dep} not in requirements.txt"


def test_env_example_has_required_vars():
    """Test that .env.example contains required environment variables."""
    with open('.env.example', 'r') as f:
        content = f.read()
    
    required_vars = [
        'SCRAPER_PLATFORM',
        'SCRAPER_USERNAME',
        'SCRAPER_PASSWORD',
        'SCRAPER_RATE_LIMIT',
        'DATABASE_URL',
        'SENTIMENT_MODEL',
    ]
    
    for var in required_vars:
        assert var in content, f"Required environment variable {var} not in .env.example"


def test_gitignore_ignores_sensitive_files():
    """Test that .gitignore includes sensitive files."""
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    sensitive_patterns = [
        '.env',
        '__pycache__',
        '*.pyc',
        'venv/',
        '*.log',
        'logs/',
    ]
    
    for pattern in sensitive_patterns:
        assert pattern in content, f"Sensitive pattern {pattern} not in .gitignore"


def test_readme_has_basic_sections():
    """Test that README.md has basic documentation sections."""
    with open('README.md', 'r') as f:
        content = f.read()
    
    required_sections = [
        '# Social Media Scraper Automation',
        '## Features',
        '## Architecture',
        '## Quick Start',
        '## Configuration',
        '## Security',
    ]
    
    for section in required_sections:
        assert section in content, f"Required section '{section}' not in README.md"


if __name__ == '__main__':
    # Run tests manually
    import pytest
    pytest.main([__file__, '-v'])
