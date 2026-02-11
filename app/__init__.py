"""
Flask Analytics Dashboard Application

This module initializes the Flask application with configuration,
logging, caching, and route registration.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
from flask_compress import Compress

# Initialize extensions
cache = Cache()
compress = Compress()


def create_app(config_name=None):
    """
    Flask application factory function.
    
    Args:
        config_name: Configuration name (not used currently, for future expansion)
    
    Returns:
        Flask application instance
    """
    # Get the project root directory (parent of 'app' package)
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create Flask app with explicit template and static folders
    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, 'templates'),
        static_folder=os.path.join(project_root, 'static')
    )
    
    # Load configuration
    from app.config import Config
    app.config.from_object(Config)
    
    # Initialize logging
    init_logging(app)
    
    # Initialize extensions
    cache.init_app(app)
    compress.init_app(app)  # Enable gzip compression
    CORS(app)  # Enable CORS for all routes
    
    # Log startup
    app.logger.info(f"Flask Analytics Dashboard starting...")
    app.logger.info(f"Debug mode: {app.config['DEBUG']}")
    app.logger.info(f"Database: {app.config['DB_NAME']} at {app.config['DB_HOST']}:{app.config['DB_PORT']}")
    
    # Initialize database connection
    from app.database import init_database, test_database_connection
    try:
        init_database(app)
        test_database_connection(app)
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {e}")
        app.logger.error("Application will continue but database operations will fail")
        # Don't raise - allow app to start for debugging purposes
    
    # Register blueprints
    from app.routes import api
    app.register_blueprint(api.api_bp)
    from app.routes import pages
    app.register_blueprint(pages.pages_bp)
    
    # Add template context processor for current year
    @app.context_processor
    def inject_now():
        return {'now': datetime.now}

    # Register error handlers
    register_error_handlers(app)
    
    # Register request logging middleware
    register_request_logging(app)
    
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
    
    Provides both JSON responses for API endpoints and HTML pages for browser requests.
    
    Args:
        app: Flask application instance
        
    Validates: Requirements 1.5, 14.1, 14.2, 14.5
    """
    from flask import request, render_template, jsonify
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors"""
        app.logger.warning(f"404 error: {request.method} {request.path} - {error}")
        
        # Return JSON for API requests
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Resource not found",
                "status": 404,
                "path": request.path,
                "timestamp": datetime.now().isoformat()
            }), 404
        
        # Return HTML page for browser requests
        return render_template(
            'error.html',
            error_code=404,
            error_title="Page Not Found",
            error_message="The page you are looking for does not exist.",
            error_details=f"Path: {request.path}",
            show_support=False
        ), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        app.logger.error(f"500 error: {request.method} {request.path} - {error}", exc_info=True)
        
        # Return JSON for API requests
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Internal server error",
                "status": 500,
                "timestamp": datetime.now().isoformat()
            }), 500
        
        # Return HTML page for browser requests
        return render_template(
            'error.html',
            error_code=500,
            error_title="Internal Server Error",
            error_message="An unexpected error occurred while processing your request.",
            error_details=None,  # Don't expose error details to users
            show_support=True
        ), 500
    
    @app.errorhandler(503)
    def service_unavailable_error(error):
        """Handle 503 Service Unavailable errors (e.g., database connection failures)"""
        app.logger.error(f"503 error: {request.method} {request.path} - {error}", exc_info=True)
        
        # Return JSON for API requests
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Service temporarily unavailable",
                "status": 503,
                "message": "Database connection failed. Please try again later.",
                "timestamp": datetime.now().isoformat()
            }), 503
        
        # Return HTML page for browser requests
        return render_template(
            'error.html',
            error_code=503,
            error_title="Service Unavailable",
            error_message="The database service is temporarily unavailable.",
            error_details="Please try again in a few moments.",
            show_support=True
        ), 503
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions"""
        # Log the full exception with stack trace
        app.logger.error(
            f"Unhandled exception: {type(error).__name__}: {str(error)}",
            exc_info=True
        )
        
        # Return JSON for API requests
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Internal server error",
                "status": 500,
                "timestamp": datetime.now().isoformat()
            }), 500
        
        # Return HTML page for browser requests
        return render_template(
            'error.html',
            error_code=500,
            error_title="Unexpected Error",
            error_message="An unexpected error occurred.",
            error_details=None,
            show_support=True
        ), 500


def register_request_logging(app):
    """
    Register request logging middleware.
    
    Logs all HTTP requests with timestamp, method, path, and response status.
    
    Args:
        app: Flask application instance
        
    Validates: Requirements 14.3
    """
    from flask import request
    from datetime import datetime
    import time
    
    @app.before_request
    def log_request_start():
        """Log request start time"""
        request.start_time = time.time()
    
    @app.after_request
    def log_request_end(response):
        """Log request completion with timing"""
        if hasattr(request, 'start_time'):
            duration_ms = int((time.time() - request.start_time) * 1000)
        else:
            duration_ms = 0
        
        # Log request details
        app.logger.info(
            f"{request.method} {request.path} - {response.status_code} ({duration_ms}ms)"
        )
        
        return response
