"""
Database Integration Module for Flask Analytics Dashboard

This module provides a wrapper around the existing database module
(database/db_connection.py and database/db_operations.py) to integrate
it with the Flask application lifecycle.

Features:
- Initialize database connection on app startup
- Connection pooling configuration
- Test database connection
- Graceful shutdown handling
- Flask application context integration

Validates Requirements: 1.2, 12.6, 15.5
"""

import logging
from flask import current_app, g
from database.db_connection import (
    DatabaseConnection,
    get_db_connection,
    close_db_connection,
    DatabaseConnectionError
)

logger = logging.getLogger(__name__)


def init_database(app):
    """
    Initialize database connection for Flask application.

    This function sets up the database connection pool using configuration
    from the Flask app config. It should be called during app initialization.
    The connection pool persists for the lifetime of the application.

    Args:
        app: Flask application instance

    Raises:
        DatabaseConnectionError: If database connection fails

    Validates: Requirements 1.2, 12.6
    """
    logger.info("Initializing database connection...")

    try:
        # Initialize the global database connection singleton
        # This creates the pool once and reuses it across all requests
        db = get_db_connection()

        # Test the connection
        if db.test_connection():
            logger.info(
                f"Database connection established successfully: "
                f"{app.config['DB_NAME']} at {app.config['DB_HOST']}:{app.config['DB_PORT']}"
            )
            logger.info(f"Connection pool: {db.min_conn}-{db.max_conn} connections")
        else:
            raise DatabaseConnectionError("Database connection test failed")

        # Register cleanup function to close connections on app shutdown only
        import atexit
        atexit.register(close_db_connection)

        return db

    except DatabaseConnectionError as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error initializing database: {e}")
        raise DatabaseConnectionError(f"Database initialization failed: {e}")


def get_db():
    """
    Get database connection for current request context.
    
    This function provides a database connection that can be used within
    Flask request handlers. It uses the global connection pool managed
    by the database module.
    
    Returns:
        DatabaseConnection: Database connection instance
        
    Example:
        @app.route('/api/posts')
        def get_posts():
            db = get_db()
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM posts")
                results = cursor.fetchall()
            return jsonify(results)
    """
    return get_db_connection()


def test_database_connection(app):
    """
    Test database connection and log the result.
    
    This function can be called during app startup to verify database
    connectivity before the application starts serving requests.
    
    Args:
        app: Flask application instance
        
    Returns:
        bool: True if connection test succeeds, False otherwise
        
    Validates: Requirements 1.2
    """
    try:
        db = get_db_connection()
        
        if db.test_connection():
            app.logger.info("[OK] Database connection test passed")
            return True
        else:
            app.logger.error("[FAIL] Database connection test failed")
            return False
            
    except DatabaseConnectionError as e:
        app.logger.error(f"[FAIL] Database connection test failed: {e}")
        return False
    except Exception as e:
        app.logger.error(f"[FAIL] Unexpected error during connection test: {e}")
        return False


def get_database_info():
    """
    Get information about the database connection.
    
    Returns:
        dict: Database connection information including pool status
        
    Example:
        {
            'connected': True,
            'pool_min': 2,
            'pool_max': 10,
            'database': 'instagram_analytics',
            'host': 'localhost',
            'port': '5432'
        }
    """
    try:
        db = get_db_connection()
        
        return {
            'connected': db.test_connection(),
            'pool_min': db.min_conn,
            'pool_max': db.max_conn,
            'database': db.database_url.split('/')[-1] if hasattr(db, 'database_url') else 'unknown',
            'host': 'configured',  # Don't expose sensitive connection details
            'port': 'configured'
        }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            'connected': False,
            'error': str(e)
        }
