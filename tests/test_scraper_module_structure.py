"""
Unit tests for Task 2.1: Scraper Module Structure

Tests the basic structure, imports, and configuration management.
Validates: Requirements 1.1, 1.5, 8.1, 8.4
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper import get_config, ConfigurationError, ScraperConfig
from scraper.main_scraper import ScraperCLI


class TestScraperImports:
    """Test that scraper module imports work correctly."""
    
    def test_import_scraper_module(self):
        """Test that scraper module can be imported."""
        import scraper
        assert hasattr(scraper, '__version__')
        assert scraper.__version__ == "0.1.0"
    
    def test_import_config_components(self):
        """Test that config components can be imported."""
        from scraper import ScraperConfig, get_config, ConfigurationError
        assert ScraperConfig is not None
        assert get_config is not None
        assert ConfigurationError is not None
    
    def test_import_main_scraper(self):
        """Test that main_scraper module can be imported."""
        from scraper.main_scraper import ScraperCLI, main
        assert ScraperCLI is not None
        assert main is not None


class TestScraperConfig:
    """Test configuration management."""
    
    def test_config_with_valid_env_vars(self):
        """Test configuration loads correctly with valid environment variables."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'instagram',
            'SCRAPER_RATE_LIMIT': '30',
            'SCRAPER_MAX_POSTS': '100',
            'SCRAPER_TIMEOUT': '300',
            'SCRAPER_HEADLESS': 'true',
            'SCRAPER_LOG_LEVEL': 'INFO',
        }):
            config = ScraperConfig(load_env=False)
            assert config.platform == 'instagram'
            assert config.rate_limit == 30
            assert config.max_posts == 100
            assert config.timeout == 300
            assert config.headless is True
            assert config.log_level == 'INFO'
    
    def test_config_missing_required_var(self):
        """Test that missing required variables raise ConfigurationError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError) as exc_info:
                ScraperConfig(load_env=False)
            
            error_msg = str(exc_info.value)
            assert 'SCRAPER_PLATFORM' in error_msg
            assert 'Missing required environment variable' in error_msg
    
    def test_config_invalid_platform(self):
        """Test that invalid platform value raises ConfigurationError."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'invalid_platform',
        }):
            with pytest.raises(ConfigurationError) as exc_info:
                ScraperConfig(load_env=False)
            
            error_msg = str(exc_info.value)
            assert 'Invalid SCRAPER_PLATFORM' in error_msg
    
    def test_config_invalid_numeric_value(self):
        """Test that invalid numeric values raise ConfigurationError."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'instagram',
            'SCRAPER_RATE_LIMIT': 'not_a_number',
        }):
            with pytest.raises(ConfigurationError) as exc_info:
                ScraperConfig(load_env=False)
            
            error_msg = str(exc_info.value)
            assert 'SCRAPER_RATE_LIMIT must be a valid integer' in error_msg
    
    def test_config_invalid_boolean_value(self):
        """Test that invalid boolean values raise ConfigurationError."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'instagram',
            'SCRAPER_HEADLESS': 'maybe',
        }):
            with pytest.raises(ConfigurationError) as exc_info:
                ScraperConfig(load_env=False)
            
            error_msg = str(exc_info.value)
            assert 'SCRAPER_HEADLESS must be a boolean value' in error_msg
    
    def test_config_invalid_log_level(self):
        """Test that invalid log level raises ConfigurationError."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'instagram',
            'SCRAPER_LOG_LEVEL': 'INVALID',
        }):
            with pytest.raises(ConfigurationError) as exc_info:
                ScraperConfig(load_env=False)
            
            error_msg = str(exc_info.value)
            assert 'SCRAPER_LOG_LEVEL must be one of' in error_msg
    
    def test_config_get_method(self):
        """Test config.get() method."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'twitter',
        }):
            config = ScraperConfig(load_env=False)
            assert config.get('SCRAPER_PLATFORM') == 'twitter'
            assert config.get('NONEXISTENT_KEY', 'default') == 'default'
    
    def test_config_has_credentials(self):
        """Test has_credentials() method."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'instagram',
            'SCRAPER_USERNAME': 'testuser',
            'SCRAPER_PASSWORD': 'testpass',
        }):
            config = ScraperConfig(load_env=False)
            assert config.has_credentials() is True
        
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'instagram',
        }):
            config = ScraperConfig(load_env=False)
            assert config.has_credentials() is False
    
    def test_config_properties(self):
        """Test all configuration properties."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'facebook',
            'SCRAPER_USERNAME': 'user123',
            'SCRAPER_PASSWORD': 'pass123',
            'SCRAPER_RATE_LIMIT': '25',
            'SCRAPER_MAX_POSTS': '200',
            'SCRAPER_TIMEOUT': '600',
            'SCRAPER_HEADLESS': 'false',
            'SCRAPER_LOG_LEVEL': 'DEBUG',
            'SCRAPER_OUTPUT_DIR': './custom_output',
        }):
            config = ScraperConfig(load_env=False)
            assert config.platform == 'facebook'
            assert config.username == 'user123'
            assert config.password == 'pass123'
            assert config.rate_limit == 25
            assert config.max_posts == 200
            assert config.timeout == 600
            assert config.headless is False
            assert config.log_level == 'DEBUG'
            assert config.output_dir == './custom_output'


class TestScraperCLI:
    """Test CLI interface."""
    
    def test_cli_help(self):
        """Test that CLI help works."""
        cli = ScraperCLI()
        with pytest.raises(SystemExit) as exc_info:
            cli.run(['--help'])
        # Help exits with code 0
        assert exc_info.value.code == 0
    
    def test_cli_version(self):
        """Test that CLI version works."""
        cli = ScraperCLI()
        with pytest.raises(SystemExit) as exc_info:
            cli.run(['--version'])
        # Version exits with code 0
        assert exc_info.value.code == 0
    
    def test_cli_missing_required_arg(self):
        """Test that missing required argument shows error."""
        cli = ScraperCLI()
        with pytest.raises(SystemExit) as exc_info:
            cli.run([])
        # Missing required arg exits with code 2
        assert exc_info.value.code == 2
    
    def test_cli_with_valid_args(self):
        """Test CLI with valid arguments."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'instagram',
        }):
            cli = ScraperCLI()
            # This should work but will show "implementation pending" message
            exit_code = cli.run(['--target', 'https://instagram.com/test'])
            assert exit_code == 0
    
    def test_cli_platform_override(self):
        """Test that CLI platform argument overrides environment."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'instagram',
        }):
            cli = ScraperCLI()
            exit_code = cli.run([
                '--platform', 'twitter',
                '--target', 'https://twitter.com/test'
            ])
            assert exit_code == 0
    
    def test_cli_output_structure(self):
        """Test that CLI creates correct output structure."""
        with patch.dict(os.environ, {
            'SCRAPER_PLATFORM': 'instagram',
        }):
            cli = ScraperCLI()
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                temp_output = f.name
            
            try:
                exit_code = cli.run([
                    '--target', 'https://instagram.com/test',
                    '--output', temp_output
                ])
                assert exit_code == 0
                
                # Verify output file was created
                assert os.path.exists(temp_output)
                
                # Verify output structure
                import json
                with open(temp_output, 'r') as f:
                    data = json.load(f)
                
                assert 'metadata' in data
                assert 'posts' in data
                assert data['metadata']['platform'] == 'instagram'
                assert data['metadata']['target_url'] == 'https://instagram.com/test'
                assert isinstance(data['posts'], list)
            
            finally:
                # Clean up
                if os.path.exists(temp_output):
                    os.unlink(temp_output)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
