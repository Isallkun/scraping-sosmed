"""
Configuration module for Flask Analytics Dashboard.

Reads configuration from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Flask application configuration class.
    
    All configuration values are read from environment variables with
    default fallbacks. Missing environment variables will trigger warnings
    in the application logs.
    """
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Server configuration
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '5000'))
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'instagram_analytics')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Cache configuration
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')  # 'simple' for dev, 'redis' for production
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))  # 5 minutes
    CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/0')
    
    # Dashboard configuration
    AUTO_REFRESH_INTERVAL = int(os.getenv('AUTO_REFRESH_INTERVAL', '30'))  # seconds
    POSTS_PER_PAGE = int(os.getenv('POSTS_PER_PAGE', '25'))
    
    # CORS configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    @classmethod
    def validate_config(cls):
        """
        Validate configuration and log warnings for missing values.
        
        Returns:
            list: List of warning messages for missing configuration
        """
        warnings = []
        
        # Check for default values that should be changed
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            warnings.append("SECRET_KEY is using default value. Set SECRET_KEY environment variable for production.")
        
        if not cls.DB_PASSWORD:
            warnings.append("DB_PASSWORD is empty. Set DB_PASSWORD environment variable if database requires authentication.")
        
        return warnings
