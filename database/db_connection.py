"""
Database Connection Module

This module provides database connectivity with connection pooling,
retry logic, and configuration management for PostgreSQL.

Features:
- Connection pooling using psycopg2
- Automatic retry logic for connection failures
- Environment variable configuration
- Connection health checks
- Graceful connection cleanup
"""

import os
import time
import logging
from typing import Optional
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool, OperationalError, DatabaseError
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors"""
    pass


class DatabaseConnection:
    """
    Database connection manager with connection pooling and retry logic.
    
    This class manages a connection pool to PostgreSQL database and provides
    methods for acquiring and releasing connections with automatic retry logic.
    """
    
    def __init__(
        self,
        min_conn: int = None,
        max_conn: int = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """
        Initialize database connection pool.
        
        Args:
            min_conn: Minimum number of connections in pool (default from env)
            max_conn: Maximum number of connections in pool (default from env)
            max_retries: Maximum number of connection retry attempts
            retry_delay: Delay in seconds between retry attempts
            
        Raises:
            DatabaseConnectionError: If required configuration is missing
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._pool: Optional[pool.SimpleConnectionPool] = None
        
        # Load configuration from environment variables
        self._load_config(min_conn, max_conn)
        
        # Initialize connection pool
        self._initialize_pool()
    
    def _load_config(self, min_conn: Optional[int], max_conn: Optional[int]):
        """
        Load database configuration from environment variables.
        
        Args:
            min_conn: Override for minimum connections
            max_conn: Override for maximum connections
            
        Raises:
            DatabaseConnectionError: If required configuration is missing
        """
        # Try to get DATABASE_URL first (preferred method)
        self.database_url = os.getenv('DATABASE_URL')
        
        # If DATABASE_URL not provided, construct from individual parameters
        if not self.database_url:
            db_host = os.getenv('DB_HOST')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')
            
            # Validate required parameters
            missing_params = []
            if not db_host:
                missing_params.append('DB_HOST')
            if not db_name:
                missing_params.append('DB_NAME')
            if not db_user:
                missing_params.append('DB_USER')
            if not db_password:
                missing_params.append('DB_PASSWORD')
            
            if missing_params:
                raise DatabaseConnectionError(
                    f"Missing required database configuration: {', '.join(missing_params)}. "
                    f"Please set DATABASE_URL or individual DB_* environment variables."
                )
            
            # Construct connection string
            self.database_url = (
                f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )
        
        # Load pool configuration
        self.min_conn = min_conn or int(os.getenv('DB_POOL_MIN_CONN', '2'))
        self.max_conn = max_conn or int(os.getenv('DB_POOL_MAX_CONN', '10'))
        self.connect_timeout = int(os.getenv('DB_CONNECT_TIMEOUT', '10'))
        
        # Validate pool configuration
        if self.min_conn < 1:
            raise DatabaseConnectionError("DB_POOL_MIN_CONN must be at least 1")
        if self.max_conn < self.min_conn:
            raise DatabaseConnectionError(
                f"DB_POOL_MAX_CONN ({self.max_conn}) must be >= "
                f"DB_POOL_MIN_CONN ({self.min_conn})"
            )
        
        logger.info(
            f"Database configuration loaded: "
            f"pool_size={self.min_conn}-{self.max_conn}, "
            f"timeout={self.connect_timeout}s"
        )
    
    def _initialize_pool(self):
        """
        Initialize the connection pool with retry logic.
        
        Raises:
            DatabaseConnectionError: If all connection attempts fail
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Initializing database connection pool "
                    f"(attempt {attempt}/{self.max_retries})..."
                )
                
                self._pool = pool.SimpleConnectionPool(
                    self.min_conn,
                    self.max_conn,
                    self.database_url,
                    connect_timeout=self.connect_timeout
                )
                
                # Test the connection
                conn = self._pool.getconn()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                    logger.info("Database connection pool initialized successfully")
                    return
                finally:
                    self._pool.putconn(conn)
                    
            except (OperationalError, DatabaseError) as e:
                last_error = e
                logger.warning(
                    f"Connection attempt {attempt}/{self.max_retries} failed: {e}"
                )
                
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(
                        f"Failed to initialize database connection pool after "
                        f"{self.max_retries} attempts"
                    )
        
        # If we get here, all attempts failed
        raise DatabaseConnectionError(
            f"Failed to connect to database after {self.max_retries} attempts. "
            f"Last error: {last_error}"
        )
    
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Returns:
            psycopg2.connection: Database connection
            
        Raises:
            DatabaseConnectionError: If pool is not initialized or no connections available
        """
        if self._pool is None:
            raise DatabaseConnectionError("Connection pool is not initialized")
        
        try:
            conn = self._pool.getconn()
            if conn is None:
                raise DatabaseConnectionError("No connections available in pool")
            return conn
        except (OperationalError, DatabaseError) as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise DatabaseConnectionError(f"Failed to get connection: {e}")
    
    def return_connection(self, conn):
        """
        Return a connection to the pool.
        
        Args:
            conn: Database connection to return
        """
        if self._pool is None:
            logger.warning("Cannot return connection: pool is not initialized")
            return
        
        try:
            self._pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error returning connection to pool: {e}")
    
    @contextmanager
    def get_cursor(self, commit: bool = False):
        """
        Context manager for getting a database cursor.
        
        This is a convenience method that handles connection acquisition,
        cursor creation, and cleanup automatically.
        
        Args:
            commit: Whether to commit the transaction on success
            
        Yields:
            psycopg2.cursor: Database cursor
            
        Example:
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO posts ...")
        """
        conn = None
        cursor = None
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            yield cursor
            
            if commit:
                conn.commit()
                
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")
            logger.error(f"Database operation failed: {e}")
            raise
            
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as close_error:
                    logger.error(f"Cursor close failed: {close_error}")
            if conn:
                self.return_connection(conn)
    
    def test_connection(self) -> bool:
        """
        Test if database connection is working.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def close_all_connections(self):
        """
        Close all connections in the pool.
        
        This should be called when shutting down the application.
        """
        if self._pool is not None:
            try:
                self._pool.closeall()
                logger.info("All database connections closed")
            except Exception as e:
                logger.error(f"Error closing connections: {e}")
            finally:
                self._pool = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close all connections"""
        self.close_all_connections()
        return False


# Global database connection instance
_db_instance: Optional[DatabaseConnection] = None


def get_db_connection() -> DatabaseConnection:
    """
    Get or create the global database connection instance.
    
    This function implements a singleton pattern to ensure only one
    connection pool is created per application instance.
    
    Returns:
        DatabaseConnection: Global database connection instance
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseConnection()
    
    return _db_instance


def close_db_connection():
    """
    Close the global database connection instance.
    
    This should be called when shutting down the application.
    """
    global _db_instance
    
    if _db_instance is not None:
        _db_instance.close_all_connections()
        _db_instance = None
