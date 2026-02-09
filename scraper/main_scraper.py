"""
Main Scraper Entry Point

CLI interface for executing social media scraping operations.
Validates: Requirements 1.1, 1.5, 1.6
"""

import argparse
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from scraper.config import get_config, ConfigurationError


class ScraperCLI:
    """
    Command-line interface for the social media scraper.
    
    Provides argument parsing and execution workflow for scraping operations.
    """
    
    def __init__(self):
        """Initialize the CLI."""
        self.parser = self._create_parser()
        self.config = None
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Create and configure argument parser.
        
        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description='Social Media Scraper - Extract data from social media platforms',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Scrape Instagram posts
  python main_scraper.py --platform instagram --target "https://instagram.com/username" --limit 50

  # Scrape Twitter with custom output
  python main_scraper.py --platform twitter --target "https://twitter.com/username" --output tweets.json

  # Use environment configuration
  python main_scraper.py --target "https://instagram.com/username"
            """
        )
        
        parser.add_argument(
            '--platform',
            type=str,
            choices=['instagram', 'twitter', 'facebook'],
            help='Social media platform to scrape (default: from SCRAPER_PLATFORM env var)'
        )
        
        parser.add_argument(
            '--target',
            type=str,
            required=True,
            help='Target URL to scrape (e.g., profile URL, hashtag URL)'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of posts to scrape (default: from SCRAPER_MAX_POSTS env var)'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (default: auto-generated in output directory)'
        )
        
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'csv'],
            default='json',
            help='Output format (default: json)'
        )
        
        parser.add_argument(
            '--headless',
            action='store_true',
            help='Run browser in headless mode (overrides SCRAPER_HEADLESS env var)'
        )
        
        parser.add_argument(
            '--no-headless',
            action='store_true',
            help='Run browser with visible UI (overrides SCRAPER_HEADLESS env var)'
        )
        
        parser.add_argument(
            '--log-level',
            type=str,
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='Logging level (default: from SCRAPER_LOG_LEVEL env var)'
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version='Social Media Scraper v0.1.0'
        )
        
        return parser
    
    def _merge_config_with_args(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        Merge command-line arguments with environment configuration.
        
        Command-line arguments take precedence over environment variables.
        
        Args:
            args: Parsed command-line arguments
        
        Returns:
            Merged configuration dictionary
        """
        config = {}
        
        # Platform
        config['platform'] = args.platform if args.platform else self.config.platform
        
        # Target URL
        config['target'] = args.target
        
        # Limit
        config['limit'] = args.limit if args.limit else self.config.max_posts
        
        # Output path
        if args.output:
            config['output'] = args.output
        else:
            # Auto-generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            platform = config['platform']
            filename = f"{platform}_posts_{timestamp}.{args.format}"
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            config['output'] = str(output_dir / filename)
        
        # Format
        config['format'] = args.format
        
        # Headless mode
        if args.headless:
            config['headless'] = True
        elif args.no_headless:
            config['headless'] = False
        else:
            config['headless'] = self.config.headless
        
        # Log level
        config['log_level'] = args.log_level if args.log_level else self.config.log_level
        
        # Other settings from environment
        config['rate_limit'] = self.config.rate_limit
        config['timeout'] = self.config.timeout
        config['username'] = self.config.username
        config['password'] = self.config.password
        
        return config
    
    def _create_output_structure(self, posts: List[Dict[str, Any]], 
                                 platform: str, target: str) -> Dict[str, Any]:
        """
        Create standardized output structure.
        
        Args:
            posts: List of scraped post dictionaries
            platform: Platform name
            target: Target URL
        
        Returns:
            Structured output dictionary with metadata and posts
        """
        return {
            'metadata': {
                'platform': platform,
                'scraped_at': datetime.utcnow().isoformat() + 'Z',
                'target_url': target,
                'total_posts': len(posts)
            },
            'posts': posts
        }
    
    def _write_output(self, data: Dict[str, Any], output_path: str, format: str):
        """
        Write scraped data to output file.
        
        Args:
            data: Data to write
            output_path: Output file path
            format: Output format ('json' or 'csv')
        
        Raises:
            IOError: If file writing fails
        """
        try:
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == 'csv':
                # CSV implementation would go here
                # For now, we'll just save as JSON
                print(f"Warning: CSV format not yet implemented, saving as JSON")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Output saved to: {output_path}")
        
        except IOError as e:
            print(f"✗ Error writing output file: {e}", file=sys.stderr)
            raise
    
    def run(self, argv: Optional[List[str]] = None) -> int:
        """
        Execute the scraper CLI.
        
        Args:
            argv: Command-line arguments (default: sys.argv[1:])
        
        Returns:
            Exit code (0 for success, non-zero for errors)
        """
        try:
            # Parse arguments
            args = self.parser.parse_args(argv)
            
            # Load configuration
            try:
                self.config = get_config()
            except ConfigurationError as e:
                print(f"✗ Configuration Error: {e}", file=sys.stderr)
                return 1
            
            # Merge config with arguments
            config = self._merge_config_with_args(args)
            
            print(f"Social Media Scraper v0.1.0")
            print(f"Platform: {config['platform']}")
            print(f"Target: {config['target']}")
            print(f"Limit: {config['limit']} posts")
            print(f"Output: {config['output']}")
            print(f"Headless: {config['headless']}")
            print()
            
            # Import appropriate scraper based on platform
            from scraper.scrapers import InstagramScraper, TwitterScraper, FacebookScraper
            
            # Select scraper class
            scraper_classes = {
                'instagram': InstagramScraper,
                'twitter': TwitterScraper,
                'facebook': FacebookScraper
            }
            
            scraper_class = scraper_classes.get(config['platform'])
            if not scraper_class:
                print(f"✗ Unsupported platform: {config['platform']}", file=sys.stderr)
                return 1
            
            # Prepare credentials
            credentials = {
                'username': config['username'],
                'password': config['password']
            }
            
            # Check if credentials are provided
            if not credentials['username'] or not credentials['password']:
                print(f"✗ Error: Credentials not found for {config['platform']}", file=sys.stderr)
                print(f"Please set SCRAPER_USERNAME and SCRAPER_PASSWORD environment variables", file=sys.stderr)
                return 1
            
            # Create scraper instance
            print(f"Initializing {config['platform']} scraper...")
            scraper = scraper_class(
                credentials=credentials,
                rate_limit=config['rate_limit'],
                timeout=config['timeout'],
                headless=config['headless']
            )
            
            # Execute scraping
            print(f"Starting scraping process...")
            start_time = datetime.now()
            
            try:
                result = scraper.scrape(
                    target_url=config['target'],
                    limit=config['limit'],
                    authenticate=True
                )
                
                end_time = datetime.now()
                execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Add execution time to metadata
                result['metadata']['execution_time_ms'] = execution_time_ms
                result['metadata']['errors_encountered'] = scraper.errors_encountered
                
                # Display summary
                print()
                print(f"✓ Scraping completed!")
                print(f"  Total posts scraped: {result['metadata']['total_posts']}")
                print(f"  Execution time: {execution_time_ms}ms")
                print(f"  Errors encountered: {result['metadata']['errors_encountered']}")
                print()
                
                # Write output
                self._write_output(result, config['output'], config['format'])
                
                print(f"✓ Scraping completed successfully")
                return 0
                
            except Exception as e:
                print(f"✗ Scraping failed: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
                
                # Try to save partial results if any posts were scraped
                if hasattr(scraper, 'posts_scraped') and scraper.posts_scraped:
                    print(f"\nAttempting to save {len(scraper.posts_scraped)} partial results...")
                    partial_data = self._create_output_structure(
                        scraper.posts_scraped,
                        config['platform'],
                        config['target']
                    )
                    partial_data['metadata']['status'] = 'partial'
                    partial_data['metadata']['error'] = str(e)
                    
                    try:
                        self._write_output(partial_data, config['output'], config['format'])
                        print(f"✓ Partial results saved")
                    except Exception as write_error:
                        print(f"✗ Failed to save partial results: {write_error}", file=sys.stderr)
                
                return 1
        
        except KeyboardInterrupt:
            print("\n✗ Scraping interrupted by user", file=sys.stderr)
            return 130
        
        except Exception as e:
            print(f"✗ Unexpected error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Main entry point for the scraper CLI."""
    cli = ScraperCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
