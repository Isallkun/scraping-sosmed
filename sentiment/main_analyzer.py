#!/usr/bin/env python3
"""
Sentiment Analyzer CLI

Command-line interface for the sentiment analysis module.
Provides argument parsing and execution workflow for analyzing
sentiment of scraped social media posts.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from sentiment.sentiment_analyzer import SentimentAnalyzer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Analyze sentiment of social media posts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze posts using VADER model
  python main_analyzer.py --input posts.json --output posts_sentiment.json
  
  # Use TextBlob model with custom batch size
  python main_analyzer.py --input posts.json --output posts_sentiment.json --model textblob --batch-size 50
  
  # Enable debug logging
  python main_analyzer.py --input posts.json --output posts_sentiment.json --verbose
        """
    )
    
    parser.add_argument(
        '--input',
        '-i',
        type=str,
        required=True,
        help='Path to input JSON file with scraped posts'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        required=True,
        help='Path to output JSON file with sentiment analysis results'
    )
    
    parser.add_argument(
        '--model',
        '-m',
        type=str,
        choices=['vader', 'textblob'],
        default='vader',
        help='Sentiment analysis model to use (default: vader)'
    )
    
    parser.add_argument(
        '--batch-size',
        '-b',
        type=int,
        default=100,
        help='Number of posts to process in each batch (default: 100)'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose debug logging'
    )
    
    return parser.parse_args()


def validate_input_file(input_path: str) -> bool:
    """
    Validate that input file exists and is readable.
    
    Args:
        input_path: Path to input file
        
    Returns:
        True if valid, False otherwise
    """
    input_file = Path(input_path)
    
    if not input_file.exists():
        logger.error(f"Input file does not exist: {input_path}")
        return False
    
    if not input_file.is_file():
        logger.error(f"Input path is not a file: {input_path}")
        return False
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if 'posts' not in data:
            logger.error("Input JSON must contain 'posts' array")
            return False
            
        if not isinstance(data['posts'], list):
            logger.error("'posts' must be an array")
            return False
            
        logger.info(f"Input file validated: {len(data['posts'])} posts found")
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in input file: {e}")
        return False
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return False


def validate_output_path(output_path: str) -> bool:
    """
    Validate that output path is writable.
    
    Args:
        output_path: Path to output file
        
    Returns:
        True if valid, False otherwise
    """
    output_file = Path(output_path)
    
    # Check if parent directory exists or can be created
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Cannot create output directory: {e}")
        return False


def main() -> int:
    """
    Main entry point for sentiment analyzer CLI.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        
        logger.info("Starting sentiment analysis CLI")
        logger.info(f"Input: {args.input}")
        logger.info(f"Output: {args.output}")
        logger.info(f"Model: {args.model}")
        logger.info(f"Batch size: {args.batch_size}")
        
        # Validate input file
        if not validate_input_file(args.input):
            logger.error("Input validation failed")
            return 2
        
        # Validate output path
        if not validate_output_path(args.output):
            logger.error("Output path validation failed")
            return 3
        
        # Validate batch size
        if args.batch_size <= 0:
            logger.error(f"Invalid batch size: {args.batch_size}. Must be positive.")
            return 2
        
        # Initialize sentiment analyzer
        try:
            analyzer = SentimentAnalyzer(
                model_type=args.model,
                batch_size=args.batch_size
            )
        except ValueError as e:
            logger.error(f"Failed to initialize analyzer: {e}")
            return 2
        
        # Execute analysis workflow
        try:
            stats = analyzer.analyze_file(args.input, args.output)
            
            # Log summary
            logger.info("=" * 60)
            logger.info("Sentiment Analysis Complete")
            logger.info("=" * 60)
            logger.info(f"Total posts processed: {stats['total_posts']}")
            logger.info(f"Errors encountered: {stats['error_count']}")
            logger.info(f"Model used: {stats['model']}")
            logger.info(f"Output written to: {args.output}")
            logger.info("=" * 60)
            
            # Return non-zero exit code if there were errors
            if stats['error_count'] > 0:
                logger.warning(f"Completed with {stats['error_count']} errors")
                return 1
            
            logger.info("Analysis completed successfully")
            return 0
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return 2
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            return 2
        except ValueError as e:
            logger.error(f"Invalid input data: {e}")
            return 2
        except IOError as e:
            logger.error(f"I/O error: {e}")
            return 3
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
            return 1
            
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
