"""
Flask Analytics Dashboard - Main Entry Point

Run this script to start the Flask development server.
For production, use a WSGI server like Gunicorn or uWSGI.
"""

import os
from app import create_app
from app.config import Config

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Validate configuration and log warnings
    warnings = Config.validate_config()
    for warning in warnings:
        app.logger.warning(warning)
    
    # Run development server
    app.logger.info(f"Starting Flask server on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
