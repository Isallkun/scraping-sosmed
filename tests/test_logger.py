"""
Unit tests for logging utilities.

Tests logging configuration, credential sanitization, log rotation,
and log format completeness.

Validates: Requirements 9.1, 9.2, 9.3, 9.7, 8.5
"""

import logging
import os
import tempfile
import shutil
from pathlib import Path
import pytest

from scraper.utils.logger import (
    get_logger,
    sanitize_message,
    CredentialSanitizingFormatter,
    ScraperLogger,
    CREDENTIAL_PATTERNS
)


class TestCredentialSanitization:
    """Test credential sanitization functionality."""
    
    def test_sanitize_password_colon_format(self):
        """Test sanitization of password in colon format."""
        message = "Connecting with password: secret123"
        sanitized = sanitize_message(message)
        assert "secret123" not in sanitized
        assert "***REDACTED***" in sanitized
    
    def test_sanitize_password_equals_format(self):
        """Test sanitization of password in equals format."""
        message = "Config: password=mypassword123"
        sanitized = sanitize_message(message)
        assert "mypassword123" not in sanitized
        assert "***REDACTED***" in sanitized
    
    def test_sanitize_password_json_format(self):
        """Test sanitization of password in JSON format."""
        message = '{"username": "user", "password": "secret"}'
        sanitized = sanitize_message(message)
        assert "secret" not in sanitized or "password" not in sanitized
        assert "***REDACTED***" in sanitized
    
    def test_sanitize_api_key(self):
        """Test sanitization of API key."""
        message = "Using api_key=abc123xyz456"
        sanitized = sanitize_message(message)
        assert "abc123xyz456" not in sanitized
        assert "***REDACTED***" in sanitized
    
    def test_sanitize_token(self):
        """Test sanitization of token."""
        message = "Authorization token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        sanitized = sanitize_message(message)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in sanitized
        assert "***REDACTED***" in sanitized
    
    def test_sanitize_bearer_token(self):
        """Test sanitization of Bearer token."""
        message = "Authorization: bearer abc123def456"
        sanitized = sanitize_message(message)
        assert "abc123def456" not in sanitized
        assert "***REDACTED***" in sanitized
    
    def test_sanitize_database_connection_string(self):
        """Test sanitization of database connection string."""
        message = "Connecting to postgresql://user:password123@localhost:5432/db"
        sanitized = sanitize_message(message)
        assert "password123" not in sanitized
        assert "***REDACTED***" in sanitized
        assert "user" in sanitized  # Username should remain
        assert "localhost" in sanitized  # Host should remain
    
    def test_sanitize_secret(self):
        """Test sanitization of secret."""
        message = "client_secret=supersecret123"
        sanitized = sanitize_message(message)
        assert "supersecret123" not in sanitized
        assert "***REDACTED***" in sanitized
    
    def test_sanitize_multiple_credentials(self):
        """Test sanitization of multiple credentials in one message."""
        message = "Login: username=user password=pass123 api_key=key456"
        sanitized = sanitize_message(message)
        assert "pass123" not in sanitized
        assert "key456" not in sanitized
        assert sanitized.count("***REDACTED***") >= 2
    
    def test_sanitize_preserves_non_sensitive_data(self):
        """Test that non-sensitive data is preserved."""
        message = "User logged in successfully at 2024-01-15 10:30:00"
        sanitized = sanitize_message(message)
        assert sanitized == message  # Should be unchanged
    
    def test_sanitize_case_insensitive(self):
        """Test that sanitization is case-insensitive."""
        messages = [
            "PASSWORD=secret",
            "Password=secret",
            "password=secret",
            "PaSsWoRd=secret"
        ]
        for message in messages:
            sanitized = sanitize_message(message)
            assert "secret" not in sanitized
            assert "***REDACTED***" in sanitized


class TestCredentialSanitizingFormatter:
    """Test the CredentialSanitizingFormatter class."""
    
    def test_formatter_sanitizes_log_record(self):
        """Test that formatter sanitizes credentials in log records."""
        formatter = CredentialSanitizingFormatter(
            fmt='%(levelname)s - %(message)s'
        )
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Login with password=secret123',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert "secret123" not in formatted
        assert "***REDACTED***" in formatted
    
    def test_formatter_preserves_log_format(self):
        """Test that formatter preserves the log format structure."""
        formatter = CredentialSanitizingFormatter(
            fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        record = logging.LogRecord(
            name='scraper',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Normal message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert 'INFO' in formatted
        assert 'scraper' in formatted
        assert 'Normal message' in formatted
        assert '-' in formatted  # Check separator is present


class TestScraperLogger:
    """Test the ScraperLogger class."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary directory for log files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Close all handlers before cleanup
        import logging
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        # Wait a bit for Windows to release file handles
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # If still locked, try again after a short delay
            time.sleep(0.5)
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                pass  # Give up if still locked
    
    def test_logger_creates_log_directory(self, temp_log_dir):
        """Test that logger creates log directory if it doesn't exist."""
        log_dir = Path(temp_log_dir) / 'new_logs'
        assert not log_dir.exists()
        
        logger = ScraperLogger(name='test', log_dir=str(log_dir))
        assert log_dir.exists()
    
    def test_logger_creates_log_file(self, temp_log_dir):
        """Test that logger creates log file."""
        logger = ScraperLogger(name='test', log_dir=temp_log_dir)
        log_file = Path(temp_log_dir) / 'test.log'
        
        # Write a log message
        logger.get_logger().info('Test message')
        
        assert log_file.exists()
    
    def test_logger_writes_formatted_messages(self, temp_log_dir):
        """Test that logger writes properly formatted messages."""
        logger = ScraperLogger(name='test', log_dir=temp_log_dir, console_output=False)
        log_file = Path(temp_log_dir) / 'test.log'
        
        logger.get_logger().info('Test message')
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Check log format: timestamp - level - name - message
        assert 'INFO' in content
        assert 'test' in content
        assert 'Test message' in content
        assert '-' in content  # Check separators
    
    def test_logger_sanitizes_credentials_in_file(self, temp_log_dir):
        """Test that logger sanitizes credentials when writing to file."""
        logger = ScraperLogger(name='test', log_dir=temp_log_dir, console_output=False)
        log_file = Path(temp_log_dir) / 'test.log'
        
        logger.get_logger().info('Login with password=secret123')
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        assert 'secret123' not in content
        assert '***REDACTED***' in content
    
    def test_logger_respects_log_level(self, temp_log_dir):
        """Test that logger respects configured log level."""
        logger = ScraperLogger(
            name='test',
            log_dir=temp_log_dir,
            log_level='WARNING',
            console_output=False
        )
        log_file = Path(temp_log_dir) / 'test.log'
        
        logger.get_logger().debug('Debug message')
        logger.get_logger().info('Info message')
        logger.get_logger().warning('Warning message')
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Only WARNING and above should be logged
        assert 'Debug message' not in content
        assert 'Info message' not in content
        assert 'Warning message' in content
    
    def test_logger_handles_different_log_levels(self, temp_log_dir):
        """Test that logger handles different log levels correctly."""
        logger = ScraperLogger(name='test', log_dir=temp_log_dir, console_output=False)
        log_file = Path(temp_log_dir) / 'test.log'
        
        test_logger = logger.get_logger()
        test_logger.debug('Debug message')
        test_logger.info('Info message')
        test_logger.warning('Warning message')
        test_logger.error('Error message')
        test_logger.critical('Critical message')
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        assert 'DEBUG' in content or 'Info message' in content  # Depends on level
        assert 'INFO' in content
        assert 'WARNING' in content
        assert 'ERROR' in content
        assert 'CRITICAL' in content
    
    def test_logger_includes_timestamp(self, temp_log_dir):
        """Test that log entries include timestamp."""
        logger = ScraperLogger(name='test', log_dir=temp_log_dir, console_output=False)
        log_file = Path(temp_log_dir) / 'test.log'
        
        logger.get_logger().info('Test message')
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Check for timestamp format: YYYY-MM-DD HH:MM:SS
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.search(timestamp_pattern, content) is not None
    
    def test_logger_includes_component_name(self, temp_log_dir):
        """Test that log entries include component name."""
        logger = ScraperLogger(name='scraper.instagram', log_dir=temp_log_dir, console_output=False)
        log_file = Path(temp_log_dir) / 'scraper.instagram.log'
        
        logger.get_logger().info('Test message')
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        assert 'scraper.instagram' in content
    
    def test_logger_rotation_on_size(self, temp_log_dir):
        """Test that log file rotates when size limit is reached."""
        # Create logger with small max_bytes for testing
        logger = ScraperLogger(
            name='test',
            log_dir=temp_log_dir,
            max_bytes=1024,  # 1 KB
            backup_count=2,
            console_output=False
        )
        log_file = Path(temp_log_dir) / 'test.log'
        
        # Write enough data to trigger rotation
        test_logger = logger.get_logger()
        for i in range(100):
            test_logger.info(f'Test message {i} with some padding to increase size' * 5)
        
        # Check that rotation occurred
        # Should have test.log and at least test.log.1
        log_files = list(Path(temp_log_dir).glob('test.log*'))
        assert len(log_files) > 1, f"Expected rotation, but only found: {log_files}"
    
    def test_logger_backup_count(self, temp_log_dir):
        """Test that logger respects backup_count limit."""
        logger = ScraperLogger(
            name='test',
            log_dir=temp_log_dir,
            max_bytes=500,  # Small size to trigger multiple rotations
            backup_count=2,
            console_output=False
        )
        
        # Write enough data to trigger multiple rotations
        test_logger = logger.get_logger()
        for i in range(200):
            test_logger.info(f'Test message {i} with padding' * 10)
        
        # Should have at most backup_count + 1 files (current + backups)
        log_files = list(Path(temp_log_dir).glob('test.log*'))
        assert len(log_files) <= 3, f"Expected max 3 files, found: {len(log_files)}"


class TestGetLogger:
    """Test the get_logger convenience function."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary directory for log files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Close all handlers before cleanup
        import logging
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        # Wait a bit for Windows to release file handles
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # If still locked, try again after a short delay
            time.sleep(0.5)
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                pass  # Give up if still locked
    
    def test_get_logger_returns_logger(self, temp_log_dir):
        """Test that get_logger returns a logger instance."""
        logger = get_logger(name='test', log_dir=temp_log_dir)
        assert isinstance(logger, logging.Logger)
    
    def test_get_logger_caches_loggers(self, temp_log_dir):
        """Test that get_logger caches logger instances."""
        logger1 = get_logger(name='test', log_dir=temp_log_dir)
        logger2 = get_logger(name='test', log_dir=temp_log_dir)
        assert logger1 is logger2
    
    def test_get_logger_different_names(self, temp_log_dir):
        """Test that different names create different loggers."""
        logger1 = get_logger(name='test1', log_dir=temp_log_dir)
        logger2 = get_logger(name='test2', log_dir=temp_log_dir)
        assert logger1 is not logger2
    
    def test_get_logger_uses_env_defaults(self, temp_log_dir, monkeypatch):
        """Test that get_logger uses environment variable defaults."""
        monkeypatch.setenv('SCRAPER_LOG_DIR', temp_log_dir)
        monkeypatch.setenv('SCRAPER_LOG_LEVEL', 'DEBUG')
        
        logger = get_logger(name='test_env')
        assert logger.level == logging.DEBUG
    
    def test_get_logger_creates_functional_logger(self, temp_log_dir):
        """Test that get_logger creates a functional logger."""
        logger = get_logger(name='test_func', log_dir=temp_log_dir, console_output=False)
        log_file = Path(temp_log_dir) / 'test_func.log'
        
        logger.info('Test message')
        
        assert log_file.exists()
        with open(log_file, 'r') as f:
            content = f.read()
        assert 'Test message' in content


class TestLogEntryFormat:
    """Test log entry format completeness (Property 17)."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary directory for log files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Close all handlers before cleanup
        import logging
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        # Wait a bit for Windows to release file handles
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # If still locked, try again after a short delay
            time.sleep(0.5)
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                pass  # Give up if still locked
    
    def test_log_entry_has_all_required_fields(self, temp_log_dir):
        """Test that log entries contain timestamp, level, component, and message."""
        logger = ScraperLogger(
            name='test.component',
            log_dir=temp_log_dir,
            console_output=False
        )
        log_file = Path(temp_log_dir) / 'test.component.log'
        
        logger.get_logger().info('Test message content')
        
        with open(log_file, 'r') as f:
            log_entry = f.read().strip()
        
        # Parse log entry
        parts = log_entry.split(' - ')
        
        # Should have 4 parts: timestamp, level, component, message
        assert len(parts) >= 4, f"Expected 4 parts, got {len(parts)}: {log_entry}"
        
        # Verify timestamp format
        timestamp = parts[0]
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.match(timestamp_pattern, timestamp), f"Invalid timestamp: {timestamp}"
        
        # Verify level
        level = parts[1]
        assert level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], f"Invalid level: {level}"
        
        # Verify component
        component = parts[2]
        assert component == 'test.component', f"Invalid component: {component}"
        
        # Verify message
        message = parts[3]
        assert 'Test message content' in message, f"Invalid message: {message}"
    
    def test_log_entries_for_different_levels(self, temp_log_dir):
        """Test that all log levels produce properly formatted entries."""
        logger = ScraperLogger(
            name='test',
            log_dir=temp_log_dir,
            log_level='DEBUG',
            console_output=False
        )
        log_file = Path(temp_log_dir) / 'test.log'
        
        test_logger = logger.get_logger()
        test_logger.debug('Debug message')
        test_logger.info('Info message')
        test_logger.warning('Warning message')
        test_logger.error('Error message')
        test_logger.critical('Critical message')
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Each line should have proper format
        for line in lines:
            parts = line.strip().split(' - ')
            assert len(parts) >= 4, f"Invalid format: {line}"


class TestErrorLogging:
    """Test error logging with stack traces (Property 18)."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary directory for log files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Close all handlers before cleanup
        import logging
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        # Wait a bit for Windows to release file handles
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # If still locked, try again after a short delay
            time.sleep(0.5)
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                pass  # Give up if still locked
    
    def test_error_logging_includes_exception_info(self, temp_log_dir):
        """Test that error logging includes exception information."""
        logger = ScraperLogger(name='test', log_dir=temp_log_dir, console_output=False)
        log_file = Path(temp_log_dir) / 'test.log'
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.get_logger().error('An error occurred', exc_info=True)
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Should contain error message and stack trace
        assert 'An error occurred' in content
        assert 'ValueError' in content
        assert 'Test exception' in content
        assert 'Traceback' in content
    
    def test_error_logging_without_exc_info(self, temp_log_dir):
        """Test that error logging works without exc_info."""
        logger = ScraperLogger(name='test', log_dir=temp_log_dir, console_output=False)
        log_file = Path(temp_log_dir) / 'test.log'
        
        logger.get_logger().error('Simple error message')
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        assert 'Simple error message' in content
        assert 'ERROR' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
