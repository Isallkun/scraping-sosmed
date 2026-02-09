"""
Configuration Management Module

Loads and validates configuration from environment variables.
Validates: Requirements 1.1, 1.5, 8.1, 8.4
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required variables."""
    pass


class ScraperConfig:
    """
    Configuration manager for the scraper module.
    
    Loads configuration from environment variables and validates required settings.
    Raises descriptive errors for missing or invalid configuration.
    """
    
    # Required environment variables
    REQUIRED_VARS = [
        'SCRAPER_PLATFORM',
    ]
    
    # Optional environment variables with defaults
    OPTIONAL_VARS = {
        'SCRAPER_RATE_LIMIT': '30',
        'SCRAPER_MAX_POSTS': '100',
        'SCRAPER_TIMEOUT': '300',
        'SCRAPER_HEADLESS': 'true',
        'SCRAPER_LOG_LEVEL': 'INFO',
        'SCRAPER_OUTPUT_DIR': './output',
    }
    
    def __init__(self, load_env: bool = True):
        """
        Initialize configuration manager.
        
        Args:
            load_env: Whether to load .env file (default: True)
        
        Raises:
            ConfigurationError: If required configuration is missing
        """
        if load_env:
            load_dotenv()
        
        self._config: Dict[str, Any] = {}
        self._load_configuration()
        self._validate_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables."""
        # Load required variables
        for var in self.REQUIRED_VARS:
            value = os.getenv(var)
            if value is not None:
                self._config[var] = value
        
        # Load optional variables with defaults
        for var, default in self.OPTIONAL_VARS.items():
            self._config[var] = os.getenv(var, default)
        
        # Load credentials (optional, may not be needed for all platforms)
        self._config['SCRAPER_USERNAME'] = os.getenv('SCRAPER_USERNAME')
        self._config['SCRAPER_PASSWORD'] = os.getenv('SCRAPER_PASSWORD')
    
    def _validate_configuration(self):
        """
        Validate that all required configuration is present.
        
        Raises:
            ConfigurationError: If required variables are missing
        """
        missing_vars = []
        
        for var in self.REQUIRED_VARS:
            if var not in self._config or self._config[var] is None:
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = (
                f"Missing required environment variable(s): {', '.join(missing_vars)}. "
                f"Please set these variables in your .env file or environment."
            )
            raise ConfigurationError(error_msg)
        
        # Validate platform value
        valid_platforms = ['instagram', 'twitter', 'facebook']
        platform = self._config.get('SCRAPER_PLATFORM', '').lower()
        if platform not in valid_platforms:
            raise ConfigurationError(
                f"Invalid SCRAPER_PLATFORM '{platform}'. "
                f"Must be one of: {', '.join(valid_platforms)}"
            )
        
        # Validate numeric values
        try:
            self._config['SCRAPER_RATE_LIMIT'] = int(self._config['SCRAPER_RATE_LIMIT'])
        except ValueError:
            raise ConfigurationError(
                f"SCRAPER_RATE_LIMIT must be a valid integer, got: {self._config['SCRAPER_RATE_LIMIT']}"
            )
        
        try:
            self._config['SCRAPER_MAX_POSTS'] = int(self._config['SCRAPER_MAX_POSTS'])
        except ValueError:
            raise ConfigurationError(
                f"SCRAPER_MAX_POSTS must be a valid integer, got: {self._config['SCRAPER_MAX_POSTS']}"
            )
        
        try:
            self._config['SCRAPER_TIMEOUT'] = int(self._config['SCRAPER_TIMEOUT'])
        except ValueError:
            raise ConfigurationError(
                f"SCRAPER_TIMEOUT must be a valid integer, got: {self._config['SCRAPER_TIMEOUT']}"
            )
        
        # Validate boolean values
        headless_str = self._config['SCRAPER_HEADLESS'].lower()
        if headless_str not in ['true', 'false', '1', '0', 'yes', 'no']:
            raise ConfigurationError(
                f"SCRAPER_HEADLESS must be a boolean value (true/false), got: {self._config['SCRAPER_HEADLESS']}"
            )
        self._config['SCRAPER_HEADLESS'] = headless_str in ['true', '1', 'yes']
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        log_level = self._config['SCRAPER_LOG_LEVEL'].upper()
        if log_level not in valid_log_levels:
            raise ConfigurationError(
                f"SCRAPER_LOG_LEVEL must be one of {', '.join(valid_log_levels)}, got: {log_level}"
            )
        self._config['SCRAPER_LOG_LEVEL'] = log_level
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration as dictionary.
        
        Returns:
            Dictionary of all configuration values
        """
        return self._config.copy()
    
    @property
    def platform(self) -> str:
        """Get the configured platform."""
        return self._config['SCRAPER_PLATFORM'].lower()
    
    @property
    def username(self) -> Optional[str]:
        """Get the configured username."""
        return self._config.get('SCRAPER_USERNAME')
    
    @property
    def password(self) -> Optional[str]:
        """Get the configured password."""
        return self._config.get('SCRAPER_PASSWORD')
    
    @property
    def rate_limit(self) -> int:
        """Get the configured rate limit (requests per minute)."""
        return self._config['SCRAPER_RATE_LIMIT']
    
    @property
    def max_posts(self) -> int:
        """Get the maximum number of posts to scrape."""
        return self._config['SCRAPER_MAX_POSTS']
    
    @property
    def timeout(self) -> int:
        """Get the maximum execution timeout in seconds."""
        return self._config['SCRAPER_TIMEOUT']
    
    @property
    def headless(self) -> bool:
        """Get whether to run browser in headless mode."""
        return self._config['SCRAPER_HEADLESS']
    
    @property
    def log_level(self) -> str:
        """Get the configured log level."""
        return self._config['SCRAPER_LOG_LEVEL']
    
    @property
    def output_dir(self) -> str:
        """Get the output directory path."""
        return self._config['SCRAPER_OUTPUT_DIR']
    
    def has_credentials(self) -> bool:
        """
        Check if credentials are configured.
        
        Returns:
            True if both username and password are set
        """
        return bool(self.username and self.password)


# Global configuration instance (lazy loaded)
_config_instance: Optional[ScraperConfig] = None


def get_config(reload: bool = False) -> ScraperConfig:
    """
    Get the global configuration instance.
    
    Args:
        reload: Whether to reload configuration from environment
    
    Returns:
        ScraperConfig instance
    
    Raises:
        ConfigurationError: If configuration is invalid
    """
    global _config_instance
    
    if _config_instance is None or reload:
        _config_instance = ScraperConfig()
    
    return _config_instance
