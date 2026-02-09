"""
Unit Tests for Main Scraper CLI

Tests the ScraperCLI class functionality including:
- Argument parsing
- Configuration merging
- Error handling

Validates: Requirements 1.6
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

from scraper.main_scraper import ScraperCLI


class TestScraperCLIArgumentParsing:
    """Test CLI argument parsing."""
    
    def test_parse_required_arguments(self):
        """Test parsing with only required arguments."""
        cli = ScraperCLI()
        args = cli.parser.parse_args(['--target', 'https://instagram.com/test'])
        
        assert args.target == 'https://instagram.com/test'
        assert args.platform is None  # Optional
        assert args.limit is None  # Optional
    
    def test_parse_all_arguments(self):
        """Test parsing with all arguments."""
        cli = ScraperCLI()
        args = cli.parser.parse_args([
            '--platform', 'instagram',
            '--target', 'https://instagram.com/test',
            '--limit', '50',
            '--output', 'output.json',
            '--format', 'json',
            '--headless',
            '--log-level', 'DEBUG'
        ])
        
        assert args.platform == 'instagram'
        assert args.target == 'https://instagram.com/test'
        assert args.limit == 50
        assert args.output == 'output.json'
        assert args.format == 'json'
        assert args.headless is True
        assert args.log_level == 'DEBUG'
    
    def test_parse_platform_choices(self):
        """Test that only valid platforms are accepted."""
        cli = ScraperCLI()
        
        # Valid platforms
        for platform in ['instagram', 'twitter', 'facebook']:
            args = cli.parser.parse_args(['--platform', platform, '--target', 'url'])
            assert args.platform == platform
        
        # Invalid platform should raise error
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['--platform', 'invalid', '--target', 'url'])
    
    def test_parse_format_choices(self):
        """Test that only valid formats are accepted."""
        cli = ScraperCLI()
        
        # Valid formats
        for fmt in ['json', 'csv']:
            args = cli.parser.parse_args(['--target', 'url', '--format', fmt])
            assert args.format == fmt
        
        # Invalid format should raise error
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['--target', 'url', '--format', 'xml'])
    
    def test_missing_required_argument(self):
        """Test that missing required argument raises error."""
        cli = ScraperCLI()
        
        # Missing --target should raise error
        with pytest.raises(SystemExit):
            cli.parser.parse_args([])
    
    def test_headless_flags(self):
        """Test headless and no-headless flags."""
        cli = ScraperCLI()
        
        # --headless flag
        args = cli.parser.parse_args(['--target', 'url', '--headless'])
        assert args.headless is True
        assert args.no_headless is False
        
        # --no-headless flag
        args = cli.parser.parse_args(['--target', 'url', '--no-headless'])
        assert args.headless is False
        assert args.no_headless is True


class TestScraperCLIConfigurationMerging:
    """Test configuration merging logic."""
    
    @patch('scraper.main_scraper.get_config')
    def test_merge_config_with_args(self, mock_get_config):
        """Test merging command-line args with environment config."""
        # Mock config
        mock_config = Mock()
        mock_config.platform = 'instagram'
        mock_config.max_posts = 100
        mock_config.headless = True
        mock_config.log_level = 'INFO'
        mock_config.rate_limit = 30
        mock_config.timeout = 300
        mock_config.username = 'test_user'
        mock_config.password = 'test_pass'
        mock_config.output_dir = './output'
        mock_get_config.return_value = mock_config
        
        cli = ScraperCLI()
        cli.config = mock_config
        
        # Parse args
        args = cli.parser.parse_args([
            '--target', 'https://instagram.com/test',
            '--limit', '50'
        ])
        
        # Merge config
        config = cli._merge_config_with_args(args)
        
        assert config['platform'] == 'instagram'
        assert config['target'] == 'https://instagram.com/test'
        assert config['limit'] == 50
        assert config['rate_limit'] == 30
        assert config['username'] == 'test_user'
    
    @patch('scraper.main_scraper.get_config')
    def test_cli_args_override_env_config(self, mock_get_config):
        """Test that CLI args override environment config."""
        # Mock config
        mock_config = Mock()
        mock_config.platform = 'instagram'
        mock_config.max_posts = 100
        mock_config.headless = True
        mock_config.log_level = 'INFO'
        mock_config.rate_limit = 30
        mock_config.timeout = 300
        mock_config.username = 'test_user'
        mock_config.password = 'test_pass'
        mock_config.output_dir = './output'
        mock_get_config.return_value = mock_config
        
        cli = ScraperCLI()
        cli.config = mock_config
        
        # Parse args with overrides
        args = cli.parser.parse_args([
            '--platform', 'twitter',
            '--target', 'https://twitter.com/test',
            '--limit', '25',
            '--no-headless',
            '--log-level', 'DEBUG'
        ])
        
        # Merge config
        config = cli._merge_config_with_args(args)
        
        # CLI args should override env config
        assert config['platform'] == 'twitter'
        assert config['limit'] == 25
        assert config['headless'] is False
        assert config['log_level'] == 'DEBUG'


class TestScraperCLIOutputStructure:
    """Test output structure creation."""
    
    def test_create_output_structure(self):
        """Test creating standardized output structure."""
        cli = ScraperCLI()
        
        posts = [
            {'post_id': '1', 'content': 'Test 1'},
            {'post_id': '2', 'content': 'Test 2'}
        ]
        
        output = cli._create_output_structure(posts, 'instagram', 'https://instagram.com/test')
        
        assert 'metadata' in output
        assert 'posts' in output
        assert output['metadata']['platform'] == 'instagram'
        assert output['metadata']['target_url'] == 'https://instagram.com/test'
        assert output['metadata']['total_posts'] == 2
        assert 'scraped_at' in output['metadata']
        assert output['posts'] == posts


class TestScraperCLIErrorHandling:
    """Test error handling."""
    
    @patch('scraper.main_scraper.get_config')
    def test_configuration_error_handling(self, mock_get_config):
        """Test handling of configuration errors."""
        from scraper.config import ConfigurationError
        
        # Mock config to raise error
        mock_get_config.side_effect = ConfigurationError("Missing SCRAPER_PLATFORM")
        
        cli = ScraperCLI()
        exit_code = cli.run(['--target', 'https://instagram.com/test'])
        
        assert exit_code == 1
    
    @patch('scraper.main_scraper.get_config')
    @patch('scraper.scrapers.InstagramScraper')
    def test_keyboard_interrupt_handling(self, mock_scraper_class, mock_get_config):
        """Test handling of keyboard interrupt."""
        mock_config = Mock()
        mock_config.platform = 'instagram'
        mock_config.max_posts = 100
        mock_config.headless = True
        mock_config.log_level = 'INFO'
        mock_config.rate_limit = 30
        mock_config.timeout = 300
        mock_config.username = 'test_user'
        mock_config.password = 'test_pass'
        mock_config.output_dir = './output'
        mock_get_config.return_value = mock_config
        
        # Mock scraper to raise KeyboardInterrupt
        mock_scraper = Mock()
        mock_scraper.scrape.side_effect = KeyboardInterrupt()
        mock_scraper_class.return_value = mock_scraper
        
        cli = ScraperCLI()
        exit_code = cli.run(['--target', 'https://instagram.com/test'])
        
        assert exit_code == 130


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
