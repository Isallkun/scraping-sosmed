"""
Unit tests for database connection module.

Tests cover:
- Configuration loading from environment variables
- Connection pool initialization
- Retry logic for connection failures
- Connection acquisition and release
- Error handling
- Context manager functionality
"""

import os
import pytest
from unittest.mock import patch, MagicMock, Mock
import psycopg2
from psycopg2 import OperationalError, DatabaseError

from database.db_connection import (
    DatabaseConnection,
    DatabaseConnectionError,
    get_db_connection,
    close_db_connection
)


class TestDatabaseConnectionConfiguration:
    """Test configuration loading from environment variables"""
    
    def test_load_config_from_database_url(self):
        """Test loading configuration from DATABASE_URL"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'DB_POOL_MIN_CONN': '2',
            'DB_POOL_MAX_CONN': '10',
            'DB_CONNECT_TIMEOUT': '10'
        }):
            with patch('database.db_connection.pool.SimpleConnectionPool'):
                db = DatabaseConnection()
                assert db.database_url == 'postgresql://user:pass@localhost:5432/testdb'
                assert db.min_conn == 2
                assert db.max_conn == 10
                assert db.connect_timeout == 10
    
    def test_load_config_from_individual_params(self):
        """Test loading configuration from individual DB_* parameters"""
        with patch.dict(os.environ, {
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'testdb',
            'DB_USER': 'testuser',
            'DB_PASSWORD': 'testpass',
            'DB_POOL_MIN_CONN': '3',
            'DB_POOL_MAX_CONN': '15'
        }, clear=True):
            with patch('database.db_connection.pool.SimpleConnectionPool'):
                db = DatabaseConnection()
                expected_url = 'postgresql://testuser:testpass@localhost:5432/testdb'
                assert db.database_url == expected_url
                assert db.min_conn == 3
                assert db.max_conn == 15
    
    def test_missing_database_url_and_params_raises_error(self):
        """Test that missing configuration raises descriptive error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(DatabaseConnectionError) as exc_info:
                DatabaseConnection()
            
            error_msg = str(exc_info.value)
            assert 'Missing required database configuration' in error_msg
            assert 'DB_HOST' in error_msg
            assert 'DB_NAME' in error_msg
            assert 'DB_USER' in error_msg
            assert 'DB_PASSWORD' in error_msg
    
    def test_missing_individual_params_raises_error(self):
        """Test that missing individual parameters are identified"""
        with patch.dict(os.environ, {
            'DB_HOST': 'localhost',
            'DB_NAME': 'testdb',
            # Missing DB_USER and DB_PASSWORD
        }, clear=True):
            with pytest.raises(DatabaseConnectionError) as exc_info:
                DatabaseConnection()
            
            error_msg = str(exc_info.value)
            assert 'DB_USER' in error_msg
            assert 'DB_PASSWORD' in error_msg
    
    def test_default_pool_configuration(self):
        """Test default pool configuration values"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }, clear=True):
            with patch('database.db_connection.pool.SimpleConnectionPool'):
                db = DatabaseConnection()
                assert db.min_conn == 2  # Default
                assert db.max_conn == 10  # Default
                assert db.connect_timeout == 10  # Default
    
    def test_override_pool_configuration(self):
        """Test overriding pool configuration via constructor"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            with patch('database.db_connection.pool.SimpleConnectionPool'):
                db = DatabaseConnection(min_conn=5, max_conn=20)
                assert db.min_conn == 5
                assert db.max_conn == 20
    
    def test_invalid_pool_min_conn_raises_error(self):
        """Test that invalid min_conn raises error"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'DB_POOL_MIN_CONN': '0'
        }):
            with pytest.raises(DatabaseConnectionError) as exc_info:
                DatabaseConnection()
            assert 'must be at least 1' in str(exc_info.value)
    
    def test_invalid_pool_max_less_than_min_raises_error(self):
        """Test that max_conn < min_conn raises error"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',
            'DB_POOL_MIN_CONN': '10',
            'DB_POOL_MAX_CONN': '5'
        }):
            with pytest.raises(DatabaseConnectionError) as exc_info:
                DatabaseConnection()
            assert 'must be >=' in str(exc_info.value)


class TestDatabaseConnectionPoolInitialization:
    """Test connection pool initialization and retry logic"""
    
    def test_successful_pool_initialization(self):
        """Test successful connection pool initialization"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            mock_pool = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_pool.getconn.return_value = mock_conn
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.execute.return_value = None
            mock_cursor.fetchone.return_value = (1,)
            
            with patch('database.db_connection.pool.SimpleConnectionPool', return_value=mock_pool):
                db = DatabaseConnection()
                assert db._pool is not None
                mock_pool.getconn.assert_called_once()
                mock_pool.putconn.assert_called_once_with(mock_conn)
    
    def test_retry_logic_on_connection_failure(self):
        """Test retry logic when connection fails"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            mock_pool = MagicMock()
            
            # First two attempts fail, third succeeds
            mock_pool.getconn.side_effect = [
                OperationalError("Connection refused"),
                OperationalError("Connection refused"),
                MagicMock()  # Success on third attempt
            ]
            
            with patch('database.db_connection.pool.SimpleConnectionPool', return_value=mock_pool):
                with patch('database.db_connection.time.sleep'):  # Skip actual sleep
                    db = DatabaseConnection(max_retries=3, retry_delay=1)
                    assert db._pool is not None
                    assert mock_pool.getconn.call_count == 3
    
    def test_all_retries_fail_raises_error(self):
        """Test that all failed retries raise DatabaseConnectionError"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            with patch('database.db_connection.pool.SimpleConnectionPool') as mock_pool_class:
                mock_pool_class.side_effect = OperationalError("Connection refused")
                
                with patch('database.db_connection.time.sleep'):
                    with pytest.raises(DatabaseConnectionError) as exc_info:
                        DatabaseConnection(max_retries=3, retry_delay=1)
                    
                    assert 'Failed to connect to database after 3 attempts' in str(exc_info.value)
                    assert mock_pool_class.call_count == 3


class TestDatabaseConnectionOperations:
    """Test connection acquisition, release, and operations"""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Fixture for mocked database connection"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            mock_pool = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_pool.getconn.return_value = mock_conn
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.execute.return_value = None
            mock_cursor.fetchone.return_value = (1,)
            
            with patch('database.db_connection.pool.SimpleConnectionPool', return_value=mock_pool):
                db = DatabaseConnection()
                yield db, mock_pool, mock_conn
    
    def test_get_connection_success(self, mock_db_connection):
        """Test successful connection acquisition"""
        db, mock_pool, mock_conn = mock_db_connection
        
        conn = db.get_connection()
        assert conn is not None
        assert conn == mock_conn
    
    def test_get_connection_when_pool_not_initialized(self):
        """Test get_connection raises error when pool is None"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            with patch('database.db_connection.pool.SimpleConnectionPool'):
                db = DatabaseConnection()
                db._pool = None  # Simulate uninitialized pool
                
                with pytest.raises(DatabaseConnectionError) as exc_info:
                    db.get_connection()
                assert 'not initialized' in str(exc_info.value)
    
    def test_get_connection_handles_operational_error(self, mock_db_connection):
        """Test get_connection handles OperationalError"""
        db, mock_pool, _ = mock_db_connection
        
        mock_pool.getconn.side_effect = OperationalError("Connection failed")
        
        with pytest.raises(DatabaseConnectionError) as exc_info:
            db.get_connection()
        assert 'Failed to get connection' in str(exc_info.value)
    
    def test_return_connection_success(self, mock_db_connection):
        """Test successful connection return"""
        db, mock_pool, mock_conn = mock_db_connection
        
        db.return_connection(mock_conn)
        mock_pool.putconn.assert_called_with(mock_conn)
    
    def test_return_connection_when_pool_not_initialized(self):
        """Test return_connection handles uninitialized pool gracefully"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            with patch('database.db_connection.pool.SimpleConnectionPool'):
                db = DatabaseConnection()
                db._pool = None
                
                # Should not raise error, just log warning
                db.return_connection(MagicMock())


class TestDatabaseConnectionContextManager:
    """Test context manager functionality"""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Fixture for mocked database connection"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            mock_pool = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_pool.getconn.return_value = mock_conn
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_conn.cursor.return_value = mock_cursor  # Direct return for non-context manager use
            mock_cursor.execute.return_value = None
            mock_cursor.fetchone.return_value = (1,)
            
            with patch('database.db_connection.pool.SimpleConnectionPool', return_value=mock_pool):
                db = DatabaseConnection()
                yield db, mock_pool, mock_conn, mock_cursor
    
    def test_get_cursor_context_manager_success(self, mock_db_connection):
        """Test get_cursor context manager successful execution"""
        db, mock_pool, mock_conn, mock_cursor = mock_db_connection
        
        # Reset the mock to track calls from this test
        mock_pool.reset_mock()
        mock_cursor.reset_mock()
        
        with db.get_cursor() as cursor:
            assert cursor is not None
            cursor.execute("SELECT 1")
        
        mock_cursor.close.assert_called_once()
        # putconn should be called twice: once during init test, once here
        assert mock_pool.putconn.call_count >= 1
    
    def test_get_cursor_with_commit(self, mock_db_connection):
        """Test get_cursor commits transaction when commit=True"""
        db, mock_pool, mock_conn, mock_cursor = mock_db_connection
        
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO test VALUES (1)")
        
        mock_conn.commit.assert_called_once()
    
    def test_get_cursor_rollback_on_error(self, mock_db_connection):
        """Test get_cursor rolls back transaction on error"""
        db, mock_pool, mock_conn, mock_cursor = mock_db_connection
        
        # Reset mocks
        mock_conn.reset_mock()
        mock_cursor.reset_mock()
        
        # Make execute raise an error
        mock_cursor.execute.side_effect = DatabaseError("Query failed")
        
        with pytest.raises(DatabaseError):
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO test VALUES (1)")
        
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()
    
    def test_database_connection_context_manager(self):
        """Test DatabaseConnection as context manager"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            mock_pool = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_pool.getconn.return_value = mock_conn
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.execute.return_value = None
            mock_cursor.fetchone.return_value = (1,)
            
            with patch('database.db_connection.pool.SimpleConnectionPool', return_value=mock_pool):
                with DatabaseConnection() as db:
                    assert db is not None
                    assert db._pool is not None
                
                # After exiting context, pool should be closed
                mock_pool.closeall.assert_called_once()


class TestDatabaseConnectionUtilities:
    """Test utility methods"""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Fixture for mocked database connection"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            mock_pool = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_pool.getconn.return_value = mock_conn
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_conn.cursor.return_value = mock_cursor  # Direct return for non-context manager use
            mock_cursor.execute.return_value = None
            mock_cursor.fetchone.return_value = (1,)
            
            with patch('database.db_connection.pool.SimpleConnectionPool', return_value=mock_pool):
                db = DatabaseConnection()
                yield db, mock_pool, mock_conn, mock_cursor
    
    def test_test_connection_success(self, mock_db_connection):
        """Test test_connection returns True on success"""
        db, mock_pool, mock_conn, mock_cursor = mock_db_connection
        
        # Reset mocks to clear initialization calls
        mock_pool.reset_mock()
        mock_cursor.reset_mock()
        
        # Set up the mock to return proper values
        mock_pool.getconn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        
        result = db.test_connection()
        assert result is True
    
    def test_test_connection_failure(self, mock_db_connection):
        """Test test_connection returns False on failure"""
        db, mock_pool, _, _ = mock_db_connection
        
        mock_pool.getconn.side_effect = OperationalError("Connection failed")
        
        result = db.test_connection()
        assert result is False
    
    def test_close_all_connections(self, mock_db_connection):
        """Test close_all_connections closes pool"""
        db, mock_pool, _, _ = mock_db_connection
        
        db.close_all_connections()
        mock_pool.closeall.assert_called_once()
        assert db._pool is None


class TestGlobalDatabaseInstance:
    """Test global database instance functions"""
    
    def teardown_method(self):
        """Clean up global instance after each test"""
        close_db_connection()
    
    def test_get_db_connection_creates_singleton(self):
        """Test get_db_connection creates singleton instance"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            with patch('database.db_connection.pool.SimpleConnectionPool'):
                db1 = get_db_connection()
                db2 = get_db_connection()
                
                assert db1 is db2  # Same instance
    
    def test_close_db_connection_closes_global_instance(self):
        """Test close_db_connection closes global instance"""
        with patch.dict(os.environ, {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'
        }):
            mock_pool = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_pool.getconn.return_value = mock_conn
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.execute.return_value = None
            mock_cursor.fetchone.return_value = (1,)
            
            with patch('database.db_connection.pool.SimpleConnectionPool', return_value=mock_pool):
                db = get_db_connection()
                assert db is not None
                
                close_db_connection()
                mock_pool.closeall.assert_called_once()
                
                # Getting connection again should create new instance
                db2 = get_db_connection()
                assert db2 is not db
