"""
Logging Utilities Module

Configures logging with rotating file handlers, credential sanitization,
and structured log formatting.

Validates: Requirements 9.1, 9.2, 9.3, 9.7, 8.5
"""

import logging
import logging.handlers
import os
import re
from typing import Optional
from pathlib import Path


# Patterns for credential sanitization
CREDENTIAL_PATTERNS = [
    # Bearer token (must come before general authorization)
    (re.compile(r'bearer\s+([a-zA-Z0-9_\-\.]+)', re.IGNORECASE), 'Bearer ***REDACTED***'),
    
    # Password patterns
    (re.compile(r'password["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'password=***REDACTED***'),
    (re.compile(r'passwd["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'passwd=***REDACTED***'),
    (re.compile(r'pwd["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'pwd=***REDACTED***'),
    
    # API key patterns
    (re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'api_key=***REDACTED***'),
    (re.compile(r'apikey["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'apikey=***REDACTED***'),
    
    # Token patterns
    (re.compile(r'token["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'token=***REDACTED***'),
    (re.compile(r'access[_-]?token["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'access_token=***REDACTED***'),
    (re.compile(r'auth[_-]?token["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'auth_token=***REDACTED***'),
    
    # Secret patterns
    (re.compile(r'secret["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'secret=***REDACTED***'),
    (re.compile(r'client[_-]?secret["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'client_secret=***REDACTED***'),
    
    # Authorization header (after bearer)
    (re.compile(r'authorization["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), 'authorization=***REDACTED***'),
    
    # Database connection strings
    (re.compile(r'://([^:]+):([^@]+)@', re.IGNORECASE), r'://\1:***REDACTED***@'),
]


class CredentialSanitizingFormatter(logging.Formatter):
    """
    Custom formatter that sanitizes credentials from log messages.
    
    Removes passwords, API keys, tokens, and other sensitive information
    from log output to prevent credential leakage.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record and sanitize any credentials.
        
        Args:
            record: Log record to format
        
        Returns:
            Formatted and sanitized log message
        """
        # Format the message first
        original_msg = super().format(record)
        
        # Sanitize credentials
        sanitized_msg = self._sanitize_credentials(original_msg)
        
        return sanitized_msg
    
    def _sanitize_credentials(self, message: str) -> str:
        """
        Remove credentials from message using regex patterns.
        
        Args:
            message: Original log message
        
        Returns:
            Sanitized message with credentials redacted
        """
        sanitized = message
        
        for pattern, replacement in CREDENTIAL_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        
        return sanitized


class ScraperLogger:
    """
    Logger configuration for the scraper application.
    
    Provides structured logging with:
    - Rotating file handler (size and time-based)
    - Console handler for development
    - Credential sanitization
    - Structured log format with timestamp, level, component, message
    """
    
    def __init__(
        self,
        name: str = 'scraper',
        log_dir: str = './logs',
        log_level: str = 'INFO',
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        console_output: bool = True
    ):
        """
        Initialize logger configuration.
        
        Args:
            name: Logger name (used as component identifier)
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Maximum size of log file before rotation (default: 10MB)
            backup_count: Number of backup log files to keep (default: 5)
            console_output: Whether to output logs to console (default: True)
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.console_output = console_output
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Set up handlers
        self._setup_file_handler()
        if self.console_output:
            self._setup_console_handler()
    
    def _setup_file_handler(self):
        """
        Set up rotating file handler with credential sanitization.
        
        Creates a RotatingFileHandler that:
        - Rotates based on file size (max_bytes)
        - Keeps backup_count old log files
        - Uses credential sanitizing formatter
        """
        log_file = self.log_dir / f'{self.name}.log'
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        
        # Set formatter with credential sanitization
        formatter = CredentialSanitizingFormatter(
            fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """
        Set up console handler for development/debugging.
        
        Creates a StreamHandler that outputs to console with
        credential sanitization.
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # Set formatter with credential sanitization
        formatter = CredentialSanitizingFormatter(
            fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.
        
        Returns:
            Configured logger instance
        """
        return self.logger


# Global logger instances cache
_loggers = {}


def get_logger(
    name: str = 'scraper',
    log_dir: Optional[str] = None,
    log_level: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    Get or create a logger instance.
    
    This function provides a convenient way to get a configured logger.
    Loggers are cached by name to avoid duplicate handlers.
    
    Args:
        name: Logger name (component identifier)
        log_dir: Directory for log files (default: './logs')
        log_level: Logging level (default: from env or 'INFO')
        max_bytes: Maximum log file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        console_output: Whether to output to console (default: True)
    
    Returns:
        Configured logger instance
    
    Example:
        >>> logger = get_logger('scraper.instagram')
        >>> logger.info('Starting Instagram scraper')
        >>> logger.error('Failed to authenticate', exc_info=True)
    """
    # Use defaults from environment if not specified
    if log_dir is None:
        log_dir = os.getenv('SCRAPER_LOG_DIR', './logs')
    
    if log_level is None:
        log_level = os.getenv('SCRAPER_LOG_LEVEL', 'INFO')
    
    # Check if logger already exists
    if name in _loggers:
        return _loggers[name]
    
    # Create new logger
    scraper_logger = ScraperLogger(
        name=name,
        log_dir=log_dir,
        log_level=log_level,
        max_bytes=max_bytes,
        backup_count=backup_count,
        console_output=console_output
    )
    
    logger = scraper_logger.get_logger()
    _loggers[name] = logger
    
    return logger


def sanitize_message(message: str) -> str:
    """
    Sanitize a message by removing credentials.
    
    This utility function can be used to manually sanitize messages
    before logging or displaying them.
    
    Args:
        message: Message to sanitize
    
    Returns:
        Sanitized message with credentials redacted
    
    Example:
        >>> msg = "Login with password=secret123"
        >>> sanitize_message(msg)
        'Login with password=***REDACTED***'
    """
    sanitized = message
    
    for pattern, replacement in CREDENTIAL_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    
    return sanitized
