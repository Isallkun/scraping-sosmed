"""
Flask Analytics Dashboard Application

This module initializes the Flask application with configuration,
logging, caching, and route registration.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS

# Initialize extensions
cache = Cache()


def create_app(config_name=None):
    """
    Flask application factory function.
    
    Args:
        config_name: Configuration name (not used currently, for future expansion)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    from app.config import Config
    app.config.from_object(Config)
    
    # Initialize logging
    init_logging(app)
    
    # Initialize extensions
    cache.init_app(app)
    CORS(app)  # Enable CORS for all routes
    
    # Log startup
    app.logger.info(f"Flask Analytics Dashboard starting...")
    app.logger.info(f"Debug mode: {app.config['DEBUG']}")
    app.logger.info(f"Database: {app.config['DB_NAME']} at {app.config['DB_HOST']}:{app.config['DB_PORT']}")
    
    # Register blueprints (will be added in later tasks)
    # from app.routes import pages, api
    # app.register_blueprint(pages.pages_bp)
    # app.register_blueprint(api.api_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def init_logging(app):
    """
    Configure logging for the Flask application.
    
    Sets up both console and rotating file handlers with appropriate
    formatting and log levels.
    
    Args:
        app: Flask application instance
    """
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set log level based on debug mode
    log_level = logging.DEBUG if app.config['DEBUG'] else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Rotating file handler (10 MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'flask_dashboard.log'),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Configure app logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    # Also configure root logger for other modules
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def register_error_handlers(app):
    """
    Register error handlers for common HTTP errors.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404 error: {error}")
        return {"error": "Resource not found", "status": 404}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 error: {error}", exc_info=True)
        return {"error": "Internal server error", "status": 500}, 500
