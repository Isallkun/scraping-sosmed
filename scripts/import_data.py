#!/usr/bin/env python3
"""
Data Import Script for Flask Analytics Dashboard

This script imports Instagram scraping data (JSON and CSV files) into the PostgreSQL database.
It supports both individual file imports and batch directory imports with upsert logic
to handle duplicate posts.

Features:
- Read JSON and CSV files from output directories
- Validate data format before insertion
- Upsert logic (insert or update) for duplicate posts
- Batch import support for multiple files
- Cache invalidation after import
- CLI interface with argparse
- Comprehensive logging

Usage:
    # Import a single JSON file
    python scripts/import_data.py --file output/instagram/raw/posts_20260209.json

    # Import all JSON files from a directory
    python scripts/import_data.py --input output/instagram/raw/ --type json

    # Import all CSV files from a directory
    python scripts/import_data.py --input output/instagram/sentiment/ --type csv

    # Batch import with verbose logging
    python scripts/import_data.py --input output/instagram/ --type json --batch --verbose

Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 10.4
"""

import argparse
import json
import csv
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path to import database module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_operations import insert_post, insert_sentiment, DatabaseOperationError
from database.db_connection import get_db_connection, DatabaseConnectionError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def read_json_file(file_path: str) -> Dict:
    """
    Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing parsed JSON data
        
    Raises:
        ValueError: If file cannot be read or parsed
        
    Validates: Requirements 9.1
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"Successfully read JSON file: {file_path}")
        return data
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {file_path}: {e}")
    except Exception as e:
        raise ValueError(f"Error reading file {file_path}: {e}")


def read_csv_file(file_path: str) -> List[Dict]:
    """
    Read and parse a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of dictionaries, one per row
        
    Raises:
        ValueError: If file cannot be read or parsed
        
    Validates: Requirements 9.1
    """
    try:
        posts = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                posts.append(row)
        logger.debug(f"Successfully read CSV file: {file_path} ({len(posts)} rows)")
        return posts
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading CSV file {file_path}: {e}")


def validate_post_data(post: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate that a post has all required fields.
    
    Required fields: post_id, author, timestamp
    
    Args:
        post: Post dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Validates: Requirements 9.7
    """
    required_fields = ['post_id', 'author', 'timestamp']
    
    for field in required_fields:
        if field not in post or not post[field]:
            return False, f"Missing required field: {field}"
    
    # Validate timestamp format
    try:
        if isinstance(post['timestamp'], str):
            datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
    except (ValueError, AttributeError) as e:
        return False, f"Invalid timestamp format: {e}"
    
    return True, None


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse timestamp string to datetime object.
    
    Args:
        timestamp_str: ISO format timestamp string
        
    Returns:
        datetime object
    """
    # Handle both 'Z' and '+00:00' timezone formats
    if isinstance(timestamp_str, str):
        timestamp_str = timestamp_str.replace('Z', '+00:00')
        return datetime.fromisoformat(timestamp_str)
    return timestamp_str


def import_post_from_json(post_data: Dict, platform: str = 'instagram') -> Optional[int]:
    """
    Import a single post from JSON data structure.
    
    Args:
        post_data: Post dictionary from JSON file
        platform: Social media platform (default: instagram)
        
    Returns:
        Database ID of inserted/updated post, or None if validation failed
        
    Validates: Requirements 9.2, 9.3, 9.7
    """
    # Validate post data
    is_valid, error_msg = validate_post_data(post_data)
    if not is_valid:
        logger.warning(f"Skipping invalid post: {error_msg}")
        return None
    
    try:
        # Extract post fields
        post_id = post_data['post_id']
        author = post_data['author']
        content = post_data.get('content', '')
        timestamp = parse_timestamp(post_data['timestamp'])
        likes = int(post_data.get('likes', 0))
        comments_count = int(post_data.get('comments_count', 0))
        shares = int(post_data.get('shares', 0))
        url = post_data.get('post_url')
        media_type = post_data.get('post_type', 'post')
        
        # Extract hashtags
        hashtags = post_data.get('hashtags', [])
        if isinstance(hashtags, str):
            # Handle comma-separated string
            hashtags = [h.strip() for h in hashtags.split(',') if h.strip()]
        
        # Insert post with upsert logic
        db_id = insert_post(
            post_id=post_id,
            platform=platform,
            author=author,
            content=content,
            timestamp=timestamp,
            likes=likes,
            comments_count=comments_count,
            shares=shares,
            url=url,
            media_type=media_type,
            hashtags=hashtags,
            raw_data=post_data
        )
        
        # Insert sentiment if available
        if 'sentiment' in post_data and post_data['sentiment']:
            sentiment = post_data['sentiment']
            try:
                insert_sentiment(
                    post_id=db_id,
                    score=float(sentiment.get('score', 0.0)),
                    label=sentiment.get('label', 'neutral'),
                    confidence=float(sentiment.get('confidence', 0.0)),
                    compound=float(sentiment.get('compound', 0.0)),
                    positive=float(sentiment.get('positive', 0.0)),
                    neutral=float(sentiment.get('neutral', 0.0)),
                    negative=float(sentiment.get('negative', 0.0)),
                    model=sentiment.get('model', 'vader')
                )
            except DatabaseOperationError as e:
                logger.warning(f"Failed to insert sentiment for post {post_id}: {e}")
        
        return db_id
        
    except (KeyError, ValueError, TypeError) as e:
        logger.warning(f"Error processing post {post_data.get('post_id', 'unknown')}: {e}")
        return None
    except DatabaseOperationError as e:
        logger.error(f"Database error importing post {post_data.get('post_id', 'unknown')}: {e}")
        return None


def import_post_from_csv(post_data: Dict, platform: str = 'instagram') -> Optional[int]:
    """
    Import a single post from CSV data structure.
    
    CSV files typically don't include sentiment data.
    
    Args:
        post_data: Post dictionary from CSV file
        platform: Social media platform (default: instagram)
        
    Returns:
        Database ID of inserted/updated post, or None if validation failed
        
    Validates: Requirements 9.2, 9.3, 9.7
    """
    # Validate post data
    is_valid, error_msg = validate_post_data(post_data)
    if not is_valid:
        logger.warning(f"Skipping invalid post: {error_msg}")
        return None
    
    try:
        # Extract post fields
        post_id = post_data['post_id']
        author = post_data['author']
        content = post_data.get('content', '')
        timestamp = parse_timestamp(post_data['timestamp'])
        likes = int(post_data.get('likes', 0))
        comments_count = int(post_data.get('comments_count', 0))
        shares = int(post_data.get('shares', 0))
        url = post_data.get('post_url', '')
        media_type = post_data.get('post_type', 'post')
        
        # Extract hashtags from string
        hashtags_str = post_data.get('hashtags', '')
        hashtags = [h.strip() for h in hashtags_str.split(',') if h.strip()] if hashtags_str else []
        
        # Insert post with upsert logic
        db_id = insert_post(
            post_id=post_id,
            platform=platform,
            author=author,
            content=content,
            timestamp=timestamp,
            likes=likes,
            comments_count=comments_count,
            shares=shares,
            url=url,
            media_type=media_type,
            hashtags=hashtags,
            raw_data=None  # CSV doesn't include full raw data
        )
        
        return db_id
        
    except (KeyError, ValueError, TypeError) as e:
        logger.warning(f"Error processing post {post_data.get('post_id', 'unknown')}: {e}")
        return None
    except DatabaseOperationError as e:
        logger.error(f"Database error importing post {post_data.get('post_id', 'unknown')}: {e}")
        return None


def import_json_file(file_path: str, platform: str = 'instagram') -> Tuple[int, int, int]:
    """
    Import posts from a JSON file.
    
    Args:
        file_path: Path to JSON file
        platform: Social media platform
        
    Returns:
        Tuple of (inserted_count, updated_count, skipped_count)
        
    Validates: Requirements 9.2, 9.4, 9.6
    """
    logger.info(f"Importing JSON file: {file_path}")
    
    try:
        data = read_json_file(file_path)
    except ValueError as e:
        logger.error(f"Failed to read file: {e}")
        return 0, 0, 0
    
    # Extract posts from JSON structure
    posts = []
    if 'posts' in data:
        posts = data['posts']
    elif isinstance(data, list):
        posts = data
    else:
        logger.error(f"Unexpected JSON structure in {file_path}")
        return 0, 0, 0
    
    inserted = 0
    skipped = 0
    
    for post in posts:
        db_id = import_post_from_json(post, platform)
        if db_id:
            inserted += 1
        else:
            skipped += 1
    
    logger.info(f"Completed {file_path}: {inserted} imported, {skipped} skipped")
    return inserted, 0, skipped  # Note: Can't distinguish insert vs update without checking


def import_csv_file(file_path: str, platform: str = 'instagram') -> Tuple[int, int, int]:
    """
    Import posts from a CSV file.
    
    Args:
        file_path: Path to CSV file
        platform: Social media platform
        
    Returns:
        Tuple of (inserted_count, updated_count, skipped_count)
        
    Validates: Requirements 9.2, 9.4, 9.6
    """
    logger.info(f"Importing CSV file: {file_path}")
    
    try:
        posts = read_csv_file(file_path)
    except ValueError as e:
        logger.error(f"Failed to read file: {e}")
        return 0, 0, 0
    
    inserted = 0
    skipped = 0
    
    for post in posts:
        db_id = import_post_from_csv(post, platform)
        if db_id:
            inserted += 1
        else:
            skipped += 1
    
    logger.info(f"Completed {file_path}: {inserted} imported, {skipped} skipped")
    return inserted, 0, skipped


def import_directory(directory: str, file_type: str, platform: str = 'instagram', 
                     recursive: bool = False) -> Tuple[int, int, int]:
    """
    Import all files of a specific type from a directory.
    
    Args:
        directory: Directory path
        file_type: File type ('json' or 'csv')
        platform: Social media platform
        recursive: Whether to search subdirectories
        
    Returns:
        Tuple of (total_inserted, total_updated, total_skipped)
        
    Validates: Requirements 9.4
    """
    logger.info(f"Importing {file_type.upper()} files from directory: {directory}")
    
    if not os.path.isdir(directory):
        logger.error(f"Directory not found: {directory}")
        return 0, 0, 0
    
    # Find all files of the specified type
    pattern = f"*.{file_type}"
    if recursive:
        files = list(Path(directory).rglob(pattern))
    else:
        files = list(Path(directory).glob(pattern))
    
    if not files:
        logger.warning(f"No {file_type.upper()} files found in {directory}")
        return 0, 0, 0
    
    logger.info(f"Found {len(files)} {file_type.upper()} files")
    
    total_inserted = 0
    total_updated = 0
    total_skipped = 0
    
    for file_path in files:
        if file_type == 'json':
            inserted, updated, skipped = import_json_file(str(file_path), platform)
        else:
            inserted, updated, skipped = import_csv_file(str(file_path), platform)
        
        total_inserted += inserted
        total_updated += updated
        total_skipped += skipped
    
    return total_inserted, total_updated, total_skipped


def invalidate_cache():
    """
    Invalidate Flask cache after data import.
    
    This ensures that the dashboard displays fresh data after import.
    
    Validates: Requirements 10.4
    """
    try:
        # Try to import Flask app and clear cache
        from app import cache
        cache.clear()
        logger.info("Cache invalidated successfully")
    except ImportError:
        logger.warning("Flask app not available, skipping cache invalidation")
    except Exception as e:
        logger.warning(f"Failed to invalidate cache: {e}")


def main():
    """
    Main CLI entry point.
    
    Validates: Requirements 9.5
    """
    parser = argparse.ArgumentParser(
        description='Import Instagram data into PostgreSQL database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import a single JSON file
  python scripts/import_data.py --file output/instagram/raw/posts_20260209.json

  # Import all JSON files from a directory
  python scripts/import_data.py --input output/instagram/raw/ --type json

  # Import all CSV files from a directory
  python scripts/import_data.py --input output/instagram/sentiment/ --type csv

  # Batch import with recursive search
  python scripts/import_data.py --input output/instagram/ --type json --batch --recursive
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--file',
        help='Path to a single JSON or CSV file to import'
    )
    input_group.add_argument(
        '--input',
        help='Directory containing files to import'
    )
    
    # File type
    parser.add_argument(
        '--type',
        choices=['json', 'csv'],
        default='json',
        help='File type to import (default: json)'
    )
    
    # Platform
    parser.add_argument(
        '--platform',
        default='instagram',
        help='Social media platform (default: instagram)'
    )
    
    # Batch options
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Batch import all files in directory'
    )
    
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Search subdirectories recursively'
    )
    
    # Logging
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Test database connection
    try:
        db = get_db_connection()
        logger.info("Database connection successful")
    except DatabaseConnectionError as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.error("Please check your database configuration in .env file")
        sys.exit(1)
    
    # Import data
    total_inserted = 0
    total_updated = 0
    total_skipped = 0
    
    try:
        if args.file:
            # Import single file
            file_ext = os.path.splitext(args.file)[1].lower()
            if file_ext == '.json':
                inserted, updated, skipped = import_json_file(args.file, args.platform)
            elif file_ext == '.csv':
                inserted, updated, skipped = import_csv_file(args.file, args.platform)
            else:
                logger.error(f"Unsupported file type: {file_ext}")
                sys.exit(1)
            
            total_inserted = inserted
            total_updated = updated
            total_skipped = skipped
        
        elif args.input:
            # Import directory
            inserted, updated, skipped = import_directory(
                args.input,
                args.type,
                args.platform,
                args.recursive
            )
            total_inserted = inserted
            total_updated = updated
            total_skipped = skipped
        
        # Invalidate cache
        invalidate_cache()
        
        # Print summary
        logger.info("=" * 60)
        logger.info("IMPORT SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total records imported: {total_inserted}")
        logger.info(f"Total records skipped:  {total_skipped}")
        logger.info("=" * 60)
        
        if total_skipped > 0:
            logger.warning(f"{total_skipped} records were skipped due to validation errors")
            logger.warning("Check the log messages above for details")
        
    except KeyboardInterrupt:
        logger.info("\nImport interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during import: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
