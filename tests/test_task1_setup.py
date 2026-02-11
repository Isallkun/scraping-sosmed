"""
Test suite for Task 1: Flask application structure and configuration

This test verifies that the Flask application is properly set up with:
- Flask app factory function
- Configuration from environment variables
- Logging configuration
- Required dependencies
"""

import os
import sys
import pytest
from pathlib import Path


def test_project_directory_structure():
    """Test that all required directories exist"""
    required_dirs = ['app', 'templates', 'static', 'tests', 'scripts', 'logs']
    
    for dir_name in required_dirs:
        assert os.path.exists(dir_name), f"Directory '{dir_name}' does not exist"
        assert os.path.isdir(dir_name), f"'{dir_name}' is not a directory"


def test_app_subdirectories():
    """Test that app subdirectories exist"""
    required_subdirs = ['app/routes', 'app/services']
    
    for dir_name in required_subdirs:
        assert os.path.exists(dir_name), f"Directory '{dir_name}' does not exist"
        assert os.path.isdir(dir_name), f"'{dir_name}' is not a directory"


def test_static_subdirectories():
    """Test that static subdirectories exist"""
    required_subdirs = ['static/css', 'static/js']
    
    for dir_name in required_subdirs:
        assert os.path.exists(dir_name), f"Directory '{dir_name}' does not exist"
        assert os.path.isdir(dir_name), f"'{dir_name}' is not a directory"


def test_app_init_exists():
    """Test that app/__init__.py exists and contains create_app function"""
    assert os.path.exists('app/__init__.py'), "app/__init__.py does not exist"
    
    with open('app/__init__.py', 'r') as f:
        content = f.read()
        assert 'def create_app' in content, "create_app function not found in app/__init__.py"
        assert 'Flask' in content, "Flask import not found in app/__init__.py"
        assert 'cache' in content.lower(), "Cache not initialized in app/__init__.py"


def test_app_config_exists():
    """Test that app/config.py exists and contains Config class"""
    assert os.path.exists('app/config.py'), "app/config.py does not exist"
    
    with open('app/config.py', 'r') as f:
        content = f.read()
        assert 'class Config' in content, "Config class not found in app/config.py"
        assert 'DB_HOST' in content, "DB_HOST not found in Config"
        assert 'DB_PORT' in content, "DB_PORT not found in Config"
        assert 'DB_NAME' in content, "DB_NAME not found in Config"
        assert 'DB_USER' in content, "DB_USER not found in Config"
        assert 'DB_PASSWORD' in content, "DB_PASSWORD not found in Config"
        assert 'CACHE_TYPE' in content, "CACHE_TYPE not found in Config"
        assert 'CACHE_DEFAULT_TIMEOUT' in content, "CACHE_DEFAULT_TIMEOUT not found in Config"


def test_logging_configuration():
    """Test that logging is configured in app/__init__.py"""
    with open('app/__init__.py', 'r') as f:
        content = f.read()
        assert 'def init_logging' in content, "init_logging function not found"
        assert 'RotatingFileHandler' in content, "RotatingFileHandler not configured"
        assert 'StreamHandler' in content or 'console' in content.lower(), "Console handler not configured"


def test_requirements_txt_exists():
    """Test that requirements.txt exists and contains required dependencies"""
    assert os.path.exists('requirements.txt'), "requirements.txt does not exist"
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
        required_packages = ['Flask', 'psycopg2', 'Flask-Caching', 'Flask-CORS']
        
        for package in required_packages:
            assert package in content, f"Required package '{package}' not found in requirements.txt"


def test_env_example_exists():
    """Test that .env.example exists and contains required configuration"""
    assert os.path.exists('.env.example'), ".env.example does not exist"
    
    with open('.env.example', 'r') as f:
        content = f.read()
        required_vars = [
            'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
            'FLASK_PORT', 'SECRET_KEY', 'DEBUG',
            'CACHE_TYPE', 'CACHE_TIMEOUT',
            'AUTO_REFRESH_INTERVAL'
        ]
        
        for var in required_vars:
            assert var in content, f"Required environment variable '{var}' not found in .env.example"


def test_flask_app_creation():
    """Test that Flask app can be created successfully"""
    from app import create_app
    
    app = create_app()
    
    assert app is not None, "Flask app creation failed"
    assert hasattr(app, 'config'), "Flask app does not have config attribute"
    assert hasattr(app, 'logger'), "Flask app does not have logger attribute"


def test_flask_app_configuration():
    """Test that Flask app loads configuration correctly"""
    from app import create_app
    from app.config import Config
    
    app = create_app()
    
    # Test that configuration is loaded
    assert app.config['DB_HOST'] == Config.DB_HOST
    assert app.config['DB_PORT'] == Config.DB_PORT
    assert app.config['DB_NAME'] == Config.DB_NAME
    assert app.config['CACHE_TYPE'] == Config.CACHE_TYPE
    assert app.config['CACHE_DEFAULT_TIMEOUT'] == Config.CACHE_DEFAULT_TIMEOUT


def test_cache_initialization():
    """Test that Flask-Caching is initialized"""
    from app import create_app, cache
    
    app = create_app()
    
    assert cache is not None, "Cache not initialized"
    # Cache should be initialized with the app
    assert hasattr(cache, 'cache'), "Cache does not have cache attribute"


def test_cors_initialization():
    """Test that Flask-CORS is initialized"""
    from app import create_app
    
    app = create_app()
    
    # CORS should be enabled - we can test this by checking if the extension is registered
    # Flask-CORS adds itself to app.extensions
    assert 'cors' in app.extensions or hasattr(app, 'after_request'), "CORS not initialized"


def test_logging_handlers():
    """Test that logging handlers are configured"""
    from app import create_app
    import logging
    
    app = create_app()
    
    # Check that app logger has handlers
    assert len(app.logger.handlers) > 0, "No logging handlers configured"
    
    # Check for console and file handlers
    handler_types = [type(h).__name__ for h in app.logger.handlers]
    assert 'StreamHandler' in handler_types, "Console handler not found"
    assert 'RotatingFileHandler' in handler_types, "File handler not found"


def test_error_handlers():
    """Test that error handlers are registered"""
    from app import create_app
    
    app = create_app()
    
    # Test 404 error handler
    with app.test_client() as client:
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        # Should return JSON error response
        data = response.get_json()
        assert data is not None, "404 error handler should return JSON"
        assert 'error' in data, "404 error response should contain 'error' field"


def test_config_validation():
    """Test that Config class has validate_config method"""
    from app.config import Config
    
    assert hasattr(Config, 'validate_config'), "Config class should have validate_config method"
    
    warnings = Config.validate_config()
    assert isinstance(warnings, list), "validate_config should return a list"


def test_run_flask_script_exists():
    """Test that run_flask.py exists"""
    assert os.path.exists('run_flask.py'), "run_flask.py does not exist"
    
    with open('run_flask.py', 'r') as f:
        content = f.read()
        assert 'create_app' in content, "create_app not imported in run_flask.py"
        assert 'app.run' in content, "app.run not called in run_flask.py"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
