"""
Data Import Service Module

This module provides functionality to import data from JSON and CSV files
into the database. It is used by the API to handle file uploads.
"""

import json
import csv
import logging
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union

from database.db_operations import (
    insert_post, 
    insert_sentiment, 
    insert_comment, 
    clear_all_data,
    DatabaseOperationError
)

# Configure logging
logger = logging.getLogger(__name__)


class ImportServiceError(Exception):
    """Custom exception for import service errors"""
    pass


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


def validate_post_data(post: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate that a post has all required fields.
    
    Args:
        post: Post dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['post_id', 'author', 'timestamp']
    
    for field in required_fields:
        if field not in post or not post[field]:
            return False, f"Missing required field: {field}"
    
    # Validate timestamp format
    try:
        if isinstance(post['timestamp'], str):
            parse_timestamp(post['timestamp'])
    except (ValueError, AttributeError) as e:
        return False, f"Invalid timestamp format: {e}"
    
    return True, None


def import_post_from_data(post_data: Dict, platform: str = 'instagram', is_json: bool = True) -> Optional[int]:
    """
    Import a single post from data dictionary.
    
    Args:
        post_data: Post dictionary
        platform: Social media platform
        is_json: Whether the source was JSON (contains full structure)
        
    Returns:
        Database ID of inserted/updated post, or None if validation failed
    """
    # Validate post data
    is_valid, error_msg = validate_post_data(post_data)
    if not is_valid:
        logger.warning(f"Skipping invalid post: {error_msg}")
        return None
    
    try:
        # Extract post fields
        post_id = str(post_data['post_id'])
        author = str(post_data['author'])
        content = str(post_data.get('content', ''))
        timestamp = parse_timestamp(post_data['timestamp'])
        
        # Handle numeric fields safely
        try:
            likes = int(post_data.get('likes', 0))
            # Try to get comments_count, fallback to length of comments array if available
            comments_count = post_data.get('comments_count')
            if comments_count is None and 'comments' in post_data and isinstance(post_data['comments'], list):
                comments_count = len(post_data['comments'])
            else:
                comments_count = int(comments_count) if comments_count is not None else 0
            shares = int(post_data.get('shares', 0))
        except (ValueError, TypeError):
            likes = 0
            comments_count = 0
            shares = 0
            
        # Handle multiple URL field names
        url = post_data.get('post_url') or post_data.get('url')
        
        # Handle multiple media_type field names with robust fallback
        # Format 1: post_type (newer format)
        # Format 2: media_type (older format)
        # Format 3: no field (default to 'post')
        media_type = post_data.get('post_type') or post_data.get('media_type')
        if not media_type or media_type == '':
            media_type = 'post'  # Default value
        
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
            raw_data=post_data if is_json else None
        )
        
        # Insert sentiment if available (JSON only usually)
        if 'sentiment' in post_data and post_data['sentiment'] and isinstance(post_data['sentiment'], dict):
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
        # Handle flattened sentiment from CSV if present
        elif 'sentiment_score' in post_data and 'sentiment_label' in post_data:
            try:
                insert_sentiment(
                    post_id=db_id,
                    score=float(post_data.get('sentiment_score', 0.0)),
                    label=post_data.get('sentiment_label', 'neutral'),
                    confidence=0.0, # Usually not in CSV export
                    compound=float(post_data.get('sentiment_score', 0.0)), # Approx
                    positive=0.0,
                    neutral=0.0,
                    negative=0.0,
                    model='unknown'
                )
            except (ValueError, DatabaseOperationError) as e:
                logger.warning(f"Failed to insert sentiment from CSV for post {post_id}: {e}")
        
        # Insert comments if available
        if 'comments' in post_data and isinstance(post_data['comments'], list):
            comments = post_data['comments']
            for comment in comments:
                if not isinstance(comment, dict):
                    continue
                    
                try:
                    c_author = str(comment.get('author') or comment.get('username') or comment.get('owner_username') or 'unknown')
                    c_content = str(comment.get('text') or comment.get('content') or '')
                    c_timestamp_str = comment.get('timestamp') or comment.get('created_at')
                    
                    if not c_content:
                        continue
                        
                    if c_timestamp_str:
                        c_timestamp = parse_timestamp(c_timestamp_str)
                    else:
                        c_timestamp = timestamp # Fallback to post timestamp
                        
                    insert_comment(
                        post_id=db_id,
                        author=c_author,
                        content=c_content,
                        timestamp=c_timestamp,
                        sentiment=None,
                        raw_data=comment
                    )
                except Exception as e:
                    logger.warning(f"Failed to insert comment for post {post_id}: {e}")

        return db_id
        
    except (KeyError, ValueError, TypeError) as e:
        logger.warning(f"Error processing post {post_data.get('post_id', 'unknown')}: {e}")
        return None
    except DatabaseOperationError as e:
        logger.error(f"Database error importing post {post_data.get('post_id', 'unknown')}: {e}")
        return None


def process_import_file(file_storage, file_type: str, platform: str = 'instagram', clear_existing: bool = True) -> Dict[str, int]:
    """
    Process an uploaded file and import its data.
    
    Args:
        file_storage: Flask FileStorage object
        file_type: 'json' or 'csv'
        platform: Social media platform
        clear_existing: If True, clear all existing data before import (default: True)
        
    Returns:
        Dict with stats: {'inserted': int, 'skipped': int, 'cleared': dict}
        
    Raises:
        ImportServiceError: If file processing fails
    """
    inserted = 0
    skipped = 0
    cleared_counts = {}
    
    try:
        # Clear existing data if requested
        if clear_existing:
            logger.info("Clearing existing database data before import...")
            try:
                cleared_counts = clear_all_data()
                logger.info(
                    f"Database cleared successfully: {cleared_counts['posts']} posts, "
                    f"{cleared_counts['sentiments']} sentiments, "
                    f"{cleared_counts['comments']} comments deleted"
                )
            except DatabaseOperationError as e:
                logger.error(f"Failed to clear database: {e}")
                raise ImportServiceError(f"Failed to clear existing data: {e}")
        
        # Read file content
        content = file_storage.read().decode('utf-8')
        
        posts = []
        is_json = False
        
        if file_type == 'json':
            try:
                data = json.loads(content)
                if isinstance(data, dict) and 'posts' in data:
                    posts = data['posts']
                elif isinstance(data, list):
                    posts = data
                else:
                    raise ImportServiceError("Invalid JSON structure. Expected list or object with 'posts' key.")
                is_json = True
            except json.JSONDecodeError as e:
                raise ImportServiceError(f"Invalid JSON format: {e}")
                
        elif file_type == 'csv':
            try:
                # Use io.StringIO to create a file-like object for csv module
                csv_file = io.StringIO(content)
                reader = csv.DictReader(csv_file)
                posts = list(reader)
                is_json = False
            except Exception as e:
                raise ImportServiceError(f"Invalid CSV format: {e}")
        
        else:
            raise ImportServiceError(f"Unsupported file type: {file_type}")
            
        logger.info(f"Processing {len(posts)} posts from uploaded {file_type.upper()} file")
        
        for post in posts:
            db_id = import_post_from_data(post, platform, is_json)
            if db_id:
                inserted += 1
            else:
                skipped += 1
                
        result = {
            'total': len(posts),
            'inserted': inserted,
            'skipped': skipped
        }
        
        # Add cleared counts if data was cleared
        if clear_existing and cleared_counts:
            result['cleared'] = cleared_counts
            
        return result
        
    except ImportServiceError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during import: {e}", exc_info=True)
        raise ImportServiceError(f"Import failed: {e}")
