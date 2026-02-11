"""
Database Operations Module

This module provides CRUD operations for posts, sentiments, and execution logs.
All operations use parameterized queries to prevent SQL injection.

Features:
- Insert operations with upsert logic for posts
- Foreign key handling for sentiments
- Query methods for reports and analytics
- Parameterized queries for security
- Transaction management
- Error handling and logging

Validates Requirements: 6.2, 6.3, 6.4, 6.5, 10.4
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

import psycopg2
from psycopg2 import sql, DatabaseError, IntegrityError
from psycopg2.extras import RealDictCursor

from database.db_connection import get_db_connection, DatabaseConnectionError


# Configure logging
logger = logging.getLogger(__name__)


class DatabaseOperationError(Exception):
    """Custom exception for database operation errors"""
    pass


def insert_post(
    post_id: str,
    platform: str,
    author: str,
    content: str,
    timestamp: datetime,
    likes: int = 0,
    comments_count: int = 0,
    shares: int = 0,
    url: Optional[str] = None,
    author_id: Optional[str] = None,
    media_type: Optional[str] = None,
    hashtags: Optional[List[str]] = None,
    raw_data: Optional[Dict] = None
) -> int:
    """
    Insert a post into the database with upsert logic.
    
    If a post with the same post_id already exists, it will be updated
    with the new data (ON CONFLICT UPDATE).
    
    Args:
        post_id: Unique identifier for the post
        platform: Social media platform (instagram, twitter, facebook)
        author: Author username
        content: Post content/caption
        timestamp: Post creation timestamp
        likes: Number of likes
        comments_count: Number of comments
        shares: Number of shares
        url: URL to the post
        author_id: Author's unique ID
        media_type: Type of media (image, video, text)
        hashtags: List of hashtags
        raw_data: Raw JSON data from scraper
        
    Returns:
        int: Database ID of the inserted/updated post
        
    Raises:
        DatabaseOperationError: If the operation fails
        
    Validates: Requirements 6.2, 6.5, 10.4
    """
    db = get_db_connection()
    
    # Prepare the upsert query with parameterized values
    query = """
        INSERT INTO posts (
            post_id, platform, author, author_id, content, timestamp,
            likes, comments_count, shares, url, media_type, hashtags, raw_data
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (post_id) DO UPDATE SET
            platform = EXCLUDED.platform,
            author = EXCLUDED.author,
            author_id = EXCLUDED.author_id,
            content = EXCLUDED.content,
            timestamp = EXCLUDED.timestamp,
            likes = EXCLUDED.likes,
            comments_count = EXCLUDED.comments_count,
            shares = EXCLUDED.shares,
            url = EXCLUDED.url,
            media_type = EXCLUDED.media_type,
            hashtags = EXCLUDED.hashtags,
            raw_data = EXCLUDED.raw_data,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id;
    """
    
    try:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    post_id, platform, author, author_id, content, timestamp,
                    likes, comments_count, shares, url, media_type,
                    hashtags, psycopg2.extras.Json(raw_data) if raw_data else None
                )
            )
            result = cursor.fetchone()
            db_id = result[0]
            
            logger.info(f"Post upserted successfully: post_id={post_id}, db_id={db_id}")
            return db_id
            
    except (DatabaseError, IntegrityError) as e:
        logger.error(f"Failed to insert post {post_id}: {e}")
        raise DatabaseOperationError(f"Failed to insert post: {e}")
    except Exception as e:
        logger.error(f"Unexpected error inserting post {post_id}: {e}")
        raise DatabaseOperationError(f"Unexpected error: {e}")


def insert_sentiment(
    post_id: int,
    score: float,
    label: str,
    confidence: float,
    compound: float,
    positive: float,
    neutral: float,
    negative: float,
    model: str = "vader"
) -> int:
    """
    Insert sentiment analysis results for a post.
    
    This function handles foreign key relationships with the posts table.
    The post must exist before inserting sentiment data.
    
    Args:
        post_id: Database ID of the post (foreign key to posts.id)
        score: Overall sentiment score
        label: Sentiment label (positive, negative, neutral)
        confidence: Confidence score
        compound: Compound sentiment score
        positive: Positive sentiment component
        neutral: Neutral sentiment component
        negative: Negative sentiment component
        model: Sentiment analysis model used (vader, textblob)
        
    Returns:
        int: Database ID of the inserted sentiment record
        
    Raises:
        DatabaseOperationError: If the operation fails or post doesn't exist
        
    Validates: Requirements 6.3, 10.4
    """
    db = get_db_connection()
    
    # Parameterized query for sentiment insertion
    query = """
        INSERT INTO sentiments (
            post_id, score, label, confidence, compound,
            positive, neutral, negative, model
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING id;
    """
    
    try:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    post_id, score, label, confidence, compound,
                    positive, neutral, negative, model
                )
            )
            result = cursor.fetchone()
            sentiment_id = result[0]
            
            logger.info(
                f"Sentiment inserted successfully: post_id={post_id}, "
                f"sentiment_id={sentiment_id}, label={label}"
            )
            return sentiment_id
            
    except IntegrityError as e:
        # Foreign key constraint violation
        if "foreign key constraint" in str(e).lower():
            logger.error(f"Post with id {post_id} does not exist")
            raise DatabaseOperationError(
                f"Cannot insert sentiment: post with id {post_id} does not exist"
            )
        else:
            logger.error(f"Integrity error inserting sentiment for post {post_id}: {e}")
            raise DatabaseOperationError(f"Integrity error: {e}")
            
    except DatabaseError as e:
        logger.error(f"Failed to insert sentiment for post {post_id}: {e}")
        raise DatabaseOperationError(f"Failed to insert sentiment: {e}")
        
    except Exception as e:
        logger.error(f"Unexpected error inserting sentiment for post {post_id}: {e}")
        raise DatabaseOperationError(f"Unexpected error: {e}")


def insert_execution_log(
    workflow_id: str,
    workflow_name: str,
    status: str,
    duration_ms: int,
    error_message: Optional[str] = None,
    error_stack: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> int:
    """
    Insert an execution log entry for workflow tracking.
    
    Args:
        workflow_id: Unique identifier for the workflow execution
        workflow_name: Name of the workflow (e.g., "daily_scraping")
        status: Execution status (success, failed, partial)
        duration_ms: Execution duration in milliseconds
        error_message: Error message if execution failed
        error_stack: Stack trace if execution failed
        metadata: Additional metadata as JSON
        
    Returns:
        int: Database ID of the inserted log entry
        
    Raises:
        DatabaseOperationError: If the operation fails
        
    Validates: Requirements 6.4, 10.4
    """
    db = get_db_connection()
    
    # Parameterized query for execution log insertion
    query = """
        INSERT INTO execution_logs (
            workflow_id, workflow_name, status, duration_ms,
            error_message, error_stack, metadata
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING id;
    """
    
    try:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    workflow_id, workflow_name, status, duration_ms,
                    error_message, error_stack,
                    psycopg2.extras.Json(metadata) if metadata else None
                )
            )
            result = cursor.fetchone()
            log_id = result[0]
            
            logger.info(
                f"Execution log inserted: workflow={workflow_name}, "
                f"status={status}, log_id={log_id}"
            )
            return log_id
            
    except DatabaseError as e:
        logger.error(
            f"Failed to insert execution log for workflow {workflow_name}: {e}"
        )
        raise DatabaseOperationError(f"Failed to insert execution log: {e}")
        
    except Exception as e:
        logger.error(
            f"Unexpected error inserting execution log for workflow {workflow_name}: {e}"
        )
        raise DatabaseOperationError(f"Unexpected error: {e}")


def get_post_by_post_id(post_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a post by its post_id.
    
    Args:
        post_id: Unique post identifier
        
    Returns:
        Dict containing post data, or None if not found
        
    Raises:
        DatabaseOperationError: If the query fails
    """
    db = get_db_connection()
    
    query = """
        SELECT * FROM posts WHERE post_id = %s;
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, (post_id,))
            result = cursor.fetchone()
            
            if result is None:
                return None
            
            # Convert tuple to dictionary
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
            
    except DatabaseError as e:
        logger.error(f"Failed to retrieve post {post_id}: {e}")
        raise DatabaseOperationError(f"Failed to retrieve post: {e}")


def get_post_by_id(db_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a post by its database ID.
    
    Args:
        db_id: Database ID of the post
        
    Returns:
        Dict containing post data, or None if not found
        
    Raises:
        DatabaseOperationError: If the query fails
    """
    db = get_db_connection()
    
    query = """
        SELECT * FROM posts WHERE id = %s;
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, (db_id,))
            result = cursor.fetchone()
            
            if result is None:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
            
    except DatabaseError as e:
        logger.error(f"Failed to retrieve post with id {db_id}: {e}")
        raise DatabaseOperationError(f"Failed to retrieve post: {e}")


def get_posts_by_date_range(
    start_date: datetime,
    end_date: datetime,
    platform: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve posts within a date range, optionally filtered by platform.
    
    Args:
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        platform: Optional platform filter
        
    Returns:
        List of post dictionaries
        
    Raises:
        DatabaseOperationError: If the query fails
        
    Validates: Requirements 6.2
    """
    db = get_db_connection()
    
    if platform:
        query = """
            SELECT * FROM posts
            WHERE timestamp >= %s AND timestamp <= %s AND platform = %s
            ORDER BY timestamp DESC;
        """
        params = (start_date, end_date, platform)
    else:
        query = """
            SELECT * FROM posts
            WHERE timestamp >= %s AND timestamp <= %s
            ORDER BY timestamp DESC;
        """
        params = (start_date, end_date)
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in results]
            
    except DatabaseError as e:
        logger.error(f"Failed to retrieve posts by date range: {e}")
        raise DatabaseOperationError(f"Failed to retrieve posts: {e}")


def get_sentiment_by_post_id(post_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve sentiment data for a specific post.
    
    Args:
        post_id: Database ID of the post
        
    Returns:
        Dict containing sentiment data, or None if not found
        
    Raises:
        DatabaseOperationError: If the query fails
    """
    db = get_db_connection()
    
    query = """
        SELECT * FROM sentiments WHERE post_id = %s;
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, (post_id,))
            result = cursor.fetchone()
            
            if result is None:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, result))
            
    except DatabaseError as e:
        logger.error(f"Failed to retrieve sentiment for post {post_id}: {e}")
        raise DatabaseOperationError(f"Failed to retrieve sentiment: {e}")


def insert_comment(
    post_id: int,
    author: str,
    content: str,
    timestamp: datetime,
    sentiment: Optional[str] = None,
    raw_data: Optional[Dict] = None
) -> int:
    """
    Insert a comment into the database.
    
    Args:
        post_id: Database ID of the parent post
        author: Comment author username
        content: Comment text
        timestamp: Comment creation timestamp
        sentiment: Optional sentiment label
        raw_data: Raw JSON data
        
    Returns:
        int: Database ID of the inserted comment
        
    Raises:
        DatabaseOperationError: If the operation fails
    """
    db = get_db_connection()
    
    query = """
        INSERT INTO comments (
            post_id, author, content, timestamp, sentiment, raw_data
        ) VALUES (
            %s, %s, %s, %s, %s, %s
        )
        RETURNING id;
    """
    
    try:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute(
                query,
                (
                    post_id, author, content, timestamp, sentiment,
                    psycopg2.extras.Json(raw_data) if raw_data else None
                )
            )
            result = cursor.fetchone()
            return result[0]
            
    except (DatabaseError, IntegrityError) as e:
        logger.error(f"Failed to insert comment for post {post_id}: {e}")
        raise DatabaseOperationError(f"Failed to insert comment: {e}")
    except Exception as e:
        logger.error(f"Unexpected error inserting comment for post {post_id}: {e}")
        raise DatabaseOperationError(f"Unexpected error: {e}")


def get_comments_by_post_id(post_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all comments for a specific post.
    
    Args:
        post_id: Database ID of the post
        
    Returns:
        List of comment dictionaries ordered by timestamp
    """
    db = get_db_connection()
    
    query = """
        SELECT * FROM comments 
        WHERE post_id = %s 
        ORDER BY timestamp ASC;
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, (post_id,))
            results = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in results]
            
    except DatabaseError as e:
        logger.error(f"Failed to retrieve comments for post {post_id}: {e}")
        raise DatabaseOperationError(f"Failed to retrieve comments: {e}")



def get_posts_with_sentiment(
    start_date: datetime,
    end_date: datetime,
    platform: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve posts with their sentiment data for a date range.
    
    This performs a JOIN between posts and sentiments tables.
    
    Args:
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        platform: Optional platform filter
        
    Returns:
        List of dictionaries containing post and sentiment data
        
    Raises:
        DatabaseOperationError: If the query fails
        
    Validates: Requirements 6.2, 6.3
    """
    db = get_db_connection()
    
    if platform:
        query = """
            SELECT 
                p.*,
                s.score, s.label, s.confidence, s.compound,
                s.positive, s.neutral, s.negative, s.model,
                s.processed_at
            FROM posts p
            LEFT JOIN sentiments s ON p.id = s.post_id
            WHERE p.timestamp >= %s AND p.timestamp <= %s AND p.platform = %s
            ORDER BY p.timestamp DESC;
        """
        params = (start_date, end_date, platform)
    else:
        query = """
            SELECT 
                p.*,
                s.score, s.label, s.confidence, s.compound,
                s.positive, s.neutral, s.negative, s.model,
                s.processed_at
            FROM posts p
            LEFT JOIN sentiments s ON p.id = s.post_id
            WHERE p.timestamp >= %s AND p.timestamp <= %s
            ORDER BY p.timestamp DESC;
        """
        params = (start_date, end_date)
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in results]
            
    except DatabaseError as e:
        logger.error(f"Failed to retrieve posts with sentiment: {e}")
        raise DatabaseOperationError(f"Failed to retrieve posts with sentiment: {e}")


def get_sentiment_distribution(
    start_date: datetime,
    end_date: datetime,
    platform: Optional[str] = None
) -> Dict[str, int]:
    """
    Get sentiment distribution (count by label) for a date range.
    
    Args:
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        platform: Optional platform filter
        
    Returns:
        Dict with sentiment labels as keys and counts as values
        Example: {"positive": 150, "neutral": 75, "negative": 25}
        
    Raises:
        DatabaseOperationError: If the query fails
        
    Validates: Requirements 6.3
    """
    db = get_db_connection()
    
    if platform:
        query = """
            SELECT s.label, COUNT(*) as count
            FROM sentiments s
            JOIN posts p ON s.post_id = p.id
            WHERE p.timestamp >= %s AND p.timestamp <= %s AND p.platform = %s
            GROUP BY s.label;
        """
        params = (start_date, end_date, platform)
    else:
        query = """
            SELECT s.label, COUNT(*) as count
            FROM sentiments s
            JOIN posts p ON s.post_id = p.id
            WHERE p.timestamp >= %s AND p.timestamp <= %s
            GROUP BY s.label;
        """
        params = (start_date, end_date)
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convert to dictionary
            distribution = {row[0]: row[1] for row in results}
            
            # Ensure all labels are present
            for label in ['positive', 'neutral', 'negative']:
                if label not in distribution:
                    distribution[label] = 0
            
            return distribution
            
    except DatabaseError as e:
        logger.error(f"Failed to get sentiment distribution: {e}")
        raise DatabaseOperationError(f"Failed to get sentiment distribution: {e}")


def get_top_posts_by_engagement(
    start_date: datetime,
    end_date: datetime,
    limit: int = 10,
    platform: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get top posts by engagement (likes + comments + shares).
    
    Args:
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        limit: Maximum number of posts to return
        platform: Optional platform filter
        
    Returns:
        List of post dictionaries ordered by engagement
        
    Raises:
        DatabaseOperationError: If the query fails
        
    Validates: Requirements 6.2
    """
    db = get_db_connection()
    
    if platform:
        query = """
            SELECT *,
                (likes + comments_count + shares) as total_engagement
            FROM posts
            WHERE timestamp >= %s AND timestamp <= %s AND platform = %s
            ORDER BY total_engagement DESC
            LIMIT %s;
        """
        params = (start_date, end_date, platform, limit)
    else:
        query = """
            SELECT *,
                (likes + comments_count + shares) as total_engagement
            FROM posts
            WHERE timestamp >= %s AND timestamp <= %s
            ORDER BY total_engagement DESC
            LIMIT %s;
        """
        params = (start_date, end_date, limit)
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in results]
            
    except DatabaseError as e:
        logger.error(f"Failed to get top posts by engagement: {e}")
        raise DatabaseOperationError(f"Failed to get top posts: {e}")


def get_execution_logs(
    workflow_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Retrieve execution logs with optional filters.
    
    Args:
        workflow_name: Optional workflow name filter
        status: Optional status filter (success, failed, partial)
        limit: Maximum number of logs to return
        
    Returns:
        List of execution log dictionaries
        
    Raises:
        DatabaseOperationError: If the query fails
        
    Validates: Requirements 6.4
    """
    db = get_db_connection()
    
    # Build query dynamically based on filters
    conditions = []
    params = []
    
    if workflow_name:
        conditions.append("workflow_name = %s")
        params.append(workflow_name)
    
    if status:
        conditions.append("status = %s")
        params.append(status)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    params.append(limit)
    
    query = f"""
        SELECT * FROM execution_logs
        WHERE {where_clause}
        ORDER BY executed_at DESC
        LIMIT %s;
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in results]
            
    except DatabaseError as e:
        logger.error(f"Failed to retrieve execution logs: {e}")
        raise DatabaseOperationError(f"Failed to retrieve execution logs: {e}")


def get_daily_post_counts(
    start_date: datetime,
    end_date: datetime,
    platform: Optional[str] = None
) -> List[Tuple[datetime, int]]:
    """
    Get daily post counts for a date range.
    
    Args:
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        platform: Optional platform filter
        
    Returns:
        List of tuples (date, count) ordered by date
        
    Raises:
        DatabaseOperationError: If the query fails
        
    Validates: Requirements 6.2
    """
    db = get_db_connection()
    
    if platform:
        query = """
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM posts
            WHERE timestamp >= %s AND timestamp <= %s AND platform = %s
            GROUP BY DATE(timestamp)
            ORDER BY date;
        """
        params = (start_date, end_date, platform)
    else:
        query = """
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM posts
            WHERE timestamp >= %s AND timestamp <= %s
            GROUP BY DATE(timestamp)
            ORDER BY date;
        """
        params = (start_date, end_date)
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
            
    except DatabaseError as e:
        logger.error(f"Failed to get daily post counts: {e}")
        raise DatabaseOperationError(f"Failed to get daily post counts: {e}")


def delete_old_posts(days: int = 90) -> int:
    """
    Delete posts older than specified number of days.
    
    This implements the data retention policy. Sentiments are automatically
    deleted via CASCADE constraint.
    
    Args:
        days: Number of days to retain (default 90)
        
    Returns:
        Number of posts deleted
        
    Raises:
        DatabaseOperationError: If the operation fails
        
    Validates: Requirements 6.7
    """
    db = get_db_connection()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    query = """
        DELETE FROM posts
        WHERE timestamp < %s
        RETURNING id;
    """
    
    try:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, (cutoff_date,))
            deleted_count = cursor.rowcount
            
            logger.info(
                f"Deleted {deleted_count} posts older than {days} days "
                f"(before {cutoff_date.date()})"
            )
            return deleted_count
            
    except DatabaseError as e:
        logger.error(f"Failed to delete old posts: {e}")
        raise DatabaseOperationError(f"Failed to delete old posts: {e}")


def delete_old_execution_logs(days: int = 30) -> int:
    """
    Delete execution logs older than specified number of days.
    
    Args:
        days: Number of days to retain (default 30)
        
    Returns:
        Number of logs deleted
        
    Raises:
        DatabaseOperationError: If the operation fails
        
    Validates: Requirements 6.7
    """
    db = get_db_connection()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    query = """
        DELETE FROM execution_logs
        WHERE executed_at < %s
        RETURNING id;
    """
    
    try:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, (cutoff_date,))
            deleted_count = cursor.rowcount
            
            logger.info(
                f"Deleted {deleted_count} execution logs older than {days} days "
                f"(before {cutoff_date.date()})"
            )
            return deleted_count
            
    except DatabaseError as e:
        logger.error(f"Failed to delete old execution logs: {e}")
        raise DatabaseOperationError(f"Failed to delete old execution logs: {e}")


def get_hashtag_frequency(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    platform: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get hashtag frequency counts from post captions.
    
    Extracts hashtags from the content field and returns the most frequent ones.
    
    Args:
        start_date: Optional start of date range (inclusive)
        end_date: Optional end of date range (inclusive)
        platform: Optional platform filter
        limit: Maximum number of hashtags to return (default 20)
        
    Returns:
        List of dictionaries with 'hashtag' and 'count' keys, ordered by count descending
        Example: [{"hashtag": "instagram", "count": 150}, {"hashtag": "photo", "count": 120}]
        
    Raises:
        DatabaseOperationError: If the query fails
        
    Validates: Requirements 6.1, 6.5
    """
    db = get_db_connection()
    
    # Build WHERE clause based on filters
    conditions = []
    params = []
    
    if start_date:
        conditions.append("timestamp >= %s")
        params.append(start_date)
    
    if end_date:
        conditions.append("timestamp <= %s")
        params.append(end_date)
    
    if platform:
        conditions.append("platform = %s")
        params.append(platform)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    params.append(limit)
    
    # Query to extract hashtags from content using regex
    # This uses PostgreSQL's regexp_matches to find all hashtags in the content
    query = f"""
        SELECT 
            LOWER(REGEXP_REPLACE(hashtag, '^#', '')) as hashtag,
            COUNT(*) as count
        FROM (
            SELECT UNNEST(REGEXP_MATCHES(content, '#(\\w+)', 'g')) as hashtag
            FROM posts
            WHERE {where_clause} AND content IS NOT NULL
        ) hashtags
        GROUP BY LOWER(REGEXP_REPLACE(hashtag, '^#', ''))
        ORDER BY count DESC
        LIMIT %s;
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            
            return [{"hashtag": row[0], "count": row[1]} for row in results]
            
    except DatabaseError as e:
        logger.error(f"Failed to get hashtag frequency: {e}")
        raise DatabaseOperationError(f"Failed to get hashtag frequency: {e}")


def get_posting_time_heatmap(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    platform: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get posting patterns by day of week and hour of day.
    
    Returns a heatmap data structure showing when posts are most frequently made.
    
    Args:
        start_date: Optional start of date range (inclusive)
        end_date: Optional end of date range (inclusive)
        platform: Optional platform filter
        
    Returns:
        List of dictionaries with 'day_of_week', 'hour', and 'count' keys
        day_of_week: 0=Sunday, 1=Monday, ..., 6=Saturday
        hour: 0-23
        Example: [{"day_of_week": 1, "hour": 14, "count": 25}, ...]
        
    Raises:
        DatabaseOperationError: If the query fails
        
    Validates: Requirements 6.2, 6.6
    """
    db = get_db_connection()
    
    # Build WHERE clause based on filters
    conditions = []
    params = []
    
    if start_date:
        conditions.append("timestamp >= %s")
        params.append(start_date)
    
    if end_date:
        conditions.append("timestamp <= %s")
        params.append(end_date)
    
    if platform:
        conditions.append("platform = %s")
        params.append(platform)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Query to group posts by day of week and hour
    # EXTRACT(DOW FROM timestamp) returns 0=Sunday, 1=Monday, etc.
    # EXTRACT(HOUR FROM timestamp) returns 0-23
    query = f"""
        SELECT 
            EXTRACT(DOW FROM timestamp)::INTEGER as day_of_week,
            EXTRACT(HOUR FROM timestamp)::INTEGER as hour,
            COUNT(*) as count
        FROM posts
        WHERE {where_clause}
        GROUP BY day_of_week, hour
        ORDER BY day_of_week, hour;
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            
            return [
                {
                    "day_of_week": row[0],
                    "hour": row[1],
                    "count": row[2]
                }
                for row in results
            ]
            
    except DatabaseError as e:
        logger.error(f"Failed to get posting time heatmap: {e}")
        raise DatabaseOperationError(f"Failed to get posting time heatmap: {e}")


def search_posts(
    search_term: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    page: int = 1,
    per_page: int = 25
) -> Dict[str, Any]:
    """
    Search and filter posts with pagination.
    
    Supports full-text search on content and author fields, plus various filters.
    
    Args:
        search_term: Optional search term to match in content or author (case-insensitive)
        filters: Optional dictionary of filters:
            - start_date: datetime - Start of date range
            - end_date: datetime - End of date range
            - platform: str - Platform filter
            - media_type: str - Media type filter
            - sentiment_label: str - Sentiment label filter (positive, neutral, negative)
            - min_likes: int - Minimum likes
            - max_likes: int - Maximum likes
            - sort_by: str - Column to sort by (default: timestamp)
            - sort_order: str - Sort order: 'asc' or 'desc' (default: desc)
        page: Page number (1-indexed)
        per_page: Number of results per page
        
    Returns:
        Dictionary with:
            - posts: List of post dictionaries with sentiment data
            - total: Total number of matching posts
            - page: Current page number
            - per_page: Results per page
            - total_pages: Total number of pages
        
    Raises:
        DatabaseOperationError: If the query fails
        
    Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.6, 7.7, 15.1, 15.2, 15.3
    """
    db = get_db_connection()
    
    if filters is None:
        filters = {}
    
    # Build WHERE clause based on search and filters
    conditions = []
    params = []
    
    # Search term (case-insensitive search in content and author)
    if search_term:
        conditions.append("(LOWER(p.content) LIKE LOWER(%s) OR LOWER(p.author) LIKE LOWER(%s))")
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern, search_pattern])
    
    # Date range filters
    if filters.get('start_date'):
        conditions.append("p.timestamp >= %s")
        params.append(filters['start_date'])
    
    if filters.get('end_date'):
        conditions.append("p.timestamp <= %s")
        params.append(filters['end_date'])
    
    # Platform filter
    if filters.get('platform'):
        conditions.append("p.platform = %s")
        params.append(filters['platform'])
    
    # Media type filter
    if filters.get('media_type'):
        conditions.append("p.media_type = %s")
        params.append(filters['media_type'])
    
    # Sentiment label filter
    if filters.get('sentiment_label'):
        conditions.append("s.label = %s")
        params.append(filters['sentiment_label'])
    
    # Likes range filters
    if filters.get('min_likes') is not None:
        conditions.append("p.likes >= %s")
        params.append(filters['min_likes'])
    
    if filters.get('max_likes') is not None:
        conditions.append("p.likes <= %s")
        params.append(filters['max_likes'])
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Sorting
    sort_by = filters.get('sort_by', 'timestamp')
    sort_order = filters.get('sort_order', 'desc').upper()
    
    # Validate sort_by to prevent SQL injection
    valid_sort_columns = [
        'timestamp', 'likes', 'comments_count', 'shares', 'author',
        'platform', 'media_type', 'score', 'label'
    ]
    if sort_by not in valid_sort_columns:
        sort_by = 'timestamp'
    
    # Validate sort_order
    if sort_order not in ['ASC', 'DESC']:
        sort_order = 'DESC'
    
    # Add table prefix for sorting
    if sort_by in ['score', 'label']:
        sort_column = f"s.{sort_by}"
    else:
        sort_column = f"p.{sort_by}"
    
    # Calculate offset for pagination
    offset = (page - 1) * per_page
    
    # Count query
    count_query = f"""
        SELECT COUNT(DISTINCT p.id)
        FROM posts p
        LEFT JOIN sentiments s ON p.id = s.post_id
        WHERE {where_clause};
    """
    
    # Data query with pagination
    data_query = f"""
        SELECT 
            p.*,
            s.score, s.label, s.confidence, s.compound,
            s.positive, s.neutral, s.negative, s.model,
            s.processed_at
        FROM posts p
        LEFT JOIN sentiments s ON p.id = s.post_id
        WHERE {where_clause}
        ORDER BY {sort_column} {sort_order}
        LIMIT %s OFFSET %s;
    """
    
    try:
        with db.get_cursor() as cursor:
            # Get total count
            cursor.execute(count_query, tuple(params))
            total = cursor.fetchone()[0]
            
            # Get paginated data
            cursor.execute(data_query, tuple(params + [per_page, offset]))
            results = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            posts = [dict(zip(columns, row)) for row in results]
            
            # Calculate total pages
            total_pages = (total + per_page - 1) // per_page if total > 0 else 0
            
            return {
                'posts': posts,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
            
    except DatabaseError as e:
        logger.error(f"Failed to search posts: {e}")
        raise DatabaseOperationError(f"Failed to search posts: {e}")


def clear_all_data() -> Dict[str, int]:
    """
    Clear all data from the database (TRUNCATE all tables).
    
    This will delete all posts, sentiments, comments, and execution logs.
    Use with caution! This operation cannot be undone.
    
    Returns:
        Dict with counts of deleted records per table
        
    Raises:
        DatabaseOperationError: If the operation fails
    """
    db = get_db_connection()
    
    try:
        counts = {}
        
        with db.get_cursor(commit=True) as cursor:
            # Get counts before deletion
            cursor.execute("SELECT COUNT(*) FROM comments")
            counts['comments'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sentiments")
            counts['sentiments'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM posts")
            counts['posts'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM execution_logs")
            counts['execution_logs'] = cursor.fetchone()[0]
            
            # Truncate tables in correct order (child tables first)
            # CASCADE will automatically delete related records
            cursor.execute("TRUNCATE TABLE comments CASCADE")
            cursor.execute("TRUNCATE TABLE sentiments CASCADE")
            cursor.execute("TRUNCATE TABLE posts CASCADE")
            cursor.execute("TRUNCATE TABLE execution_logs CASCADE")
            
            # Reset sequences to start from 1
            cursor.execute("ALTER SEQUENCE comments_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE sentiments_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE posts_id_seq RESTART WITH 1")
            cursor.execute("ALTER SEQUENCE execution_logs_id_seq RESTART WITH 1")
        
        logger.warning(
            f"Database cleared: {counts['posts']} posts, "
            f"{counts['sentiments']} sentiments, "
            f"{counts['comments']} comments, "
            f"{counts['execution_logs']} execution logs"
        )
        
        return counts
        
    except DatabaseError as e:
        logger.error(f"Failed to clear database: {e}")
        raise DatabaseOperationError(f"Failed to clear database: {e}")
    except Exception as e:
        logger.error(f"Unexpected error clearing database: {e}")
        raise DatabaseOperationError(f"Unexpected error: {e}")
