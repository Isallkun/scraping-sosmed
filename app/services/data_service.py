"""
Data Service Module

This module provides business logic for data queries and transformations
for the Flask Analytics Dashboard. It interfaces with the database module
and transforms data for visualization components.

Features:
- Summary statistics aggregation
- Sentiment analysis data transformation
- Engagement metrics calculation
- Content analysis (hashtags, posting patterns)
- Paginated post queries with search and filters

Validates Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.6,
                        5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 7.1
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter

from database.db_operations import (
    get_posts_with_sentiment,
    get_sentiment_distribution,
    get_top_posts_by_engagement,
    get_posts_by_date_range,
    get_execution_logs,
    get_comments_by_post_id,
    get_post_by_post_id,
    DatabaseOperationError
)
from database.db_connection import get_db_connection
from app.services.utils import (
    classify_sentiment,
    calculate_engagement_rate,
    extract_hashtags
)


# Configure logging
logger = logging.getLogger(__name__)


class DataServiceError(Exception):
    """Custom exception for data service errors"""
    pass


def _parse_end_date(date_str):
    """Parse end date and set to end of day if no time component."""
    if not date_str:
        return None
    dt = datetime.fromisoformat(date_str)
    # If it's a date-only string (midnight), set to end of day to be inclusive
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0 and dt.microsecond == 0:
        dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    return dt


def get_summary_stats() -> Dict[str, Any]:
    """
    Get overall statistics for the home page.
    
    Returns summary statistics including:
    - Total post count
    - Total comment count
    - Average sentiment score
    - Last execution timestamp
    - Post type distribution (posts vs reels)
    
    Returns:
        Dict containing:
            - total_posts (int): Total number of posts
            - total_comments (int): Total number of comments
            - avg_sentiment (float): Average sentiment score
            - last_execution (str): ISO timestamp of last execution
            - post_type_distribution (dict): Count by media type
    
    Raises:
        DataServiceError: If the query fails
        
    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
    """
    try:
        db = get_db_connection()

        # Get total posts, avg likes, avg comments in one query
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*),
                       COALESCE(SUM(comments_count), 0),
                       COALESCE(AVG(likes), 0),
                       COALESCE(AVG(comments_count), 0),
                       COALESCE(SUM(likes), 0),
                       COALESCE(SUM(shares), 0)
                FROM posts
            """)
            row = cursor.fetchone()
            total_posts = row[0]
            total_comments = row[1]
            avg_likes = float(row[2])
            avg_comments = float(row[3])
            total_likes = row[4]
            total_shares = row[5]

        # Get average sentiment score
        with db.get_cursor() as cursor:
            cursor.execute("SELECT AVG(score) FROM sentiments")
            result = cursor.fetchone()[0]
            avg_sentiment = float(result) if result is not None else 0.0

        # Get last execution info as object
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT executed_at, status, metadata
                FROM execution_logs
                ORDER BY executed_at DESC
                LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                metadata = result[2] if result[2] else {}
                last_execution = {
                    'timestamp': result[0].isoformat() if result[0] else None,
                    'posts_scraped': metadata.get('posts_scraped', 0) if isinstance(metadata, dict) else 0,
                    'status': result[1] if result[1] else 'unknown'
                }
            else:
                last_execution = None

        # Get post type distribution
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT media_type, COUNT(*) as count
                FROM posts
                WHERE media_type IS NOT NULL
                GROUP BY media_type
            """)
            results = cursor.fetchall()
            post_type_distribution = {row[0]: row[1] for row in results}

        # Get activity timeline (daily post and comment counts, last 30 days)
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT DATE(timestamp) as date,
                       COUNT(*) as posts,
                       COALESCE(SUM(comments_count), 0) as comments
                FROM posts
                WHERE timestamp >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(timestamp)
                ORDER BY date
            """)
            results = cursor.fetchall()
            activity_timeline = [
                {
                    'date': row[0].isoformat(),
                    'posts': row[1],
                    'comments': row[2]
                }
                for row in results
            ]

        # Calculate engagement rate
        total_engagement = total_likes + total_comments + total_shares
        engagement_rate = round((total_engagement / total_posts) if total_posts > 0 else 0, 2)

        logger.info(
            f"Summary stats retrieved: {total_posts} posts, "
            f"{total_comments} comments, avg sentiment {avg_sentiment:.3f}"
        )

        return {
            'total_posts': total_posts,
            'total_comments': total_comments,
            'avg_sentiment': round(avg_sentiment, 3),
            'last_execution': last_execution,
            'post_type_distribution': post_type_distribution,
            'activity_timeline': activity_timeline,
            'avg_likes': round(avg_likes, 1),
            'avg_comments': round(avg_comments, 1),
            'engagement_rate': engagement_rate,
            'total_reach': total_likes + total_comments
        }

    except DatabaseOperationError as e:
        logger.error(f"Database error getting summary stats: {e}")
        raise DataServiceError(f"Failed to get summary stats: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting summary stats: {e}")
        raise DataServiceError(f"Unexpected error: {e}")


def get_sentiment_data(start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get sentiment distribution and trends for visualization.
    
    Classifies sentiments as positive (score > 0.05), neutral (-0.05 to 0.05),
    or negative (score < -0.05) and provides trend data over time.
    
    Args:
        start_date: Optional start date in ISO format (YYYY-MM-DD)
        end_date: Optional end date in ISO format (YYYY-MM-DD)
    
    Returns:
        Dict containing:
            - distribution (dict): Count and percentage by sentiment category
            - trends (list): Daily sentiment scores [{date, score}]
            - gauge (float): Average sentiment score
    
    Raises:
        DataServiceError: If the query fails
        
    Validates: Requirements 4.1, 4.2, 4.3, 4.6
    """
    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = _parse_end_date(end_date)

        # Default to last 30 days if no dates provided
        if not start_dt:
            start_dt = datetime.now() - timedelta(days=30)
        if not end_dt:
            end_dt = datetime.now()

        # Get sentiment distribution
        distribution_raw = get_sentiment_distribution(start_dt, end_dt)
        
        # Calculate total and percentages
        total = sum(distribution_raw.values())
        distribution = {
            'positive': distribution_raw.get('positive', 0),
            'neutral': distribution_raw.get('neutral', 0),
            'negative': distribution_raw.get('negative', 0),
            'positive_pct': round((distribution_raw.get('positive', 0) / total * 100) if total > 0 else 0, 1),
            'neutral_pct': round((distribution_raw.get('neutral', 0) / total * 100) if total > 0 else 0, 1),
            'negative_pct': round((distribution_raw.get('negative', 0) / total * 100) if total > 0 else 0, 1)
        }
        
        # Get sentiment trends over time
        db = get_db_connection()
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT DATE(p.timestamp) as date, AVG(s.score) as avg_score
                FROM posts p
                JOIN sentiments s ON p.id = s.post_id
                WHERE p.timestamp >= %s AND p.timestamp <= %s
                GROUP BY DATE(p.timestamp)
                ORDER BY date
            """, (start_dt, end_dt))
            results = cursor.fetchall()
            trends = [
                {'date': row[0].isoformat(), 'score': round(float(row[1]), 3)}
                for row in results
            ]
        
        # Get average sentiment for gauge
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT AVG(s.score)
                FROM posts p
                JOIN sentiments s ON p.id = s.post_id
                WHERE p.timestamp >= %s AND p.timestamp <= %s
            """, (start_dt, end_dt))
            result = cursor.fetchone()[0]
            gauge = round(float(result), 3) if result is not None else 0.0
        
        # Get sentiment breakdown by post type
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT p.media_type,
                       SUM(CASE WHEN s.score > 0.05 THEN 1 ELSE 0 END) as positive,
                       SUM(CASE WHEN s.score BETWEEN -0.05 AND 0.05 THEN 1 ELSE 0 END) as neutral,
                       SUM(CASE WHEN s.score < -0.05 THEN 1 ELSE 0 END) as negative
                FROM posts p
                JOIN sentiments s ON p.id = s.post_id
                WHERE p.timestamp >= %s AND p.timestamp <= %s
                  AND p.media_type IS NOT NULL
                GROUP BY p.media_type
            """, (start_dt, end_dt))
            results = cursor.fetchall()
            by_type = {}
            for row in results:
                by_type[row[0]] = {
                    'positive': row[1],
                    'neutral': row[2],
                    'negative': row[3]
                }

        logger.info(
            f"Sentiment data retrieved: {total} posts, "
            f"avg score {gauge}, date range {start_dt.date()} to {end_dt.date()}"
        )

        return {
            'distribution': distribution,
            'trends': trends,
            'gauge': gauge,
            'by_type': by_type
        }
        
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise DataServiceError(f"Invalid date format: {e}")
    except DatabaseOperationError as e:
        logger.error(f"Database error getting sentiment data: {e}")
        raise DataServiceError(f"Failed to get sentiment data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting sentiment data: {e}")
        raise DataServiceError(f"Unexpected error: {e}")


def get_engagement_data(start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get engagement metrics and top posts.
    
    Calculates engagement rate as (likes + comments) / followers * 100
    for posts that have follower data. Returns top posts and trends.
    
    Args:
        start_date: Optional start date in ISO format (YYYY-MM-DD)
        end_date: Optional end date in ISO format (YYYY-MM-DD)
    
    Returns:
        Dict containing:
            - top_posts (list): Top 10 posts by engagement
            - trends (list): Daily engagement rates [{date, engagement_rate}]
            - type_distribution (dict): Count by post type
    
    Raises:
        DataServiceError: If the query fails
        
    Validates: Requirements 5.1, 5.2, 5.3
    """
    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = _parse_end_date(end_date)

        # Default to last 30 days if no dates provided
        if not start_dt:
            start_dt = datetime.now() - timedelta(days=30)
        if not end_dt:
            end_dt = datetime.now()

        db = get_db_connection()

        # Get engagement summary stats
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(SUM(likes), 0),
                       COALESCE(SUM(comments_count), 0),
                       COALESCE(AVG(likes + comments_count + shares), 0)
                FROM posts
                WHERE timestamp >= %s AND timestamp <= %s
            """, (start_dt, end_dt))
            row = cursor.fetchone()
            total_likes = row[0]
            total_comments_eng = row[1]
            avg_engagement_rate = round(float(row[2]), 2)

        # Get top posts by engagement
        top_posts_raw = get_top_posts_by_engagement(start_dt, end_dt, limit=10)

        # Transform top posts data
        top_posts = []
        best_post_engagement = 0
        for post in top_posts_raw:
            engagement = post.get('likes', 0) + post.get('comments_count', 0) + post.get('shares', 0)
            if engagement > best_post_engagement:
                best_post_engagement = engagement
            content = post.get('content', '') or ''
            top_posts.append({
                'post_id': post.get('post_id'),
                'author': post.get('author'),
                'content': content[:100] + '...' if len(content) > 100 else content,
                'caption': content[:100] + '...' if len(content) > 100 else content,
                'likes': post.get('likes', 0),
                'comments': post.get('comments_count', 0),
                'shares': post.get('shares', 0),
                'engagement': engagement,
                'engagement_rate': engagement,
                'total_interactions': engagement,
                'post_type': post.get('media_type', 'post'),
                'media_type': post.get('media_type', 'post'),
                'timestamp': post.get('timestamp').isoformat() if post.get('timestamp') else None,
                'url': post.get('url')
            })

        # Get engagement trends over time
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT DATE(timestamp) as date,
                       AVG(likes + comments_count + shares) as avg_engagement
                FROM posts
                WHERE timestamp >= %s AND timestamp <= %s
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (start_dt, end_dt))
            results = cursor.fetchall()
            trends = [
                {
                    'date': row[0].isoformat(),
                    'engagement': round(float(row[1]), 2),
                    'engagement_rate': round(float(row[1]), 2)
                }
                for row in results
            ]

        # Get post type distribution
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT media_type, COUNT(*) as count
                FROM posts
                WHERE timestamp >= %s AND timestamp <= %s
                  AND media_type IS NOT NULL
                GROUP BY media_type
            """, (start_dt, end_dt))
            results = cursor.fetchall()
            type_distribution = {row[0]: row[1] for row in results}

        # Get scatter data (likes vs comments for all posts)
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT likes, comments_count
                FROM posts
                WHERE timestamp >= %s AND timestamp <= %s
            """, (start_dt, end_dt))
            results = cursor.fetchall()
            scatter_data = [
                {'likes': row[0], 'comments': row[1]}
                for row in results
            ]

        logger.info(
            f"Engagement data retrieved: {len(top_posts)} top posts, "
            f"date range {start_dt.date()} to {end_dt.date()}"
        )

        return {
            'top_posts': top_posts,
            'trends': trends,
            'type_distribution': type_distribution,
            'avg_engagement_rate': avg_engagement_rate,
            'total_likes': total_likes,
            'total_comments': total_comments_eng,
            'best_post_rate': best_post_engagement,
            'scatter_data': scatter_data
        }
        
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise DataServiceError(f"Invalid date format: {e}")
    except DatabaseOperationError as e:
        logger.error(f"Database error getting engagement data: {e}")
        raise DataServiceError(f"Failed to get engagement data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting engagement data: {e}")
        raise DataServiceError(f"Unexpected error: {e}")


def get_content_data(start_date: Optional[str] = None,
                     end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get content analysis data including hashtags and posting patterns.
    
    Extracts hashtags from post content, analyzes posting patterns by
    day of week and hour, and provides content length distribution.
    
    Args:
        start_date: Optional start date in ISO format (YYYY-MM-DD)
        end_date: Optional end date in ISO format (YYYY-MM-DD)
    
    Returns:
        Dict containing:
            - hashtags (list): Top 20 hashtags [{tag, count}]
            - posting_heatmap (list): Posts by day/hour [{day, hour, count}]
            - length_distribution (list): Content length bins [{bin, count}]
    
    Raises:
        DataServiceError: If the query fails
        
    Validates: Requirements 6.1, 6.2, 6.3
    """
    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = _parse_end_date(end_date)

        # Default to last 30 days if no dates provided
        if not start_dt:
            start_dt = datetime.now() - timedelta(days=30)
        if not end_dt:
            end_dt = datetime.now()

        db = get_db_connection()

        # Get posts for hashtag extraction
        posts = get_posts_by_date_range(start_dt, end_dt)
        
        # Extract and count hashtags, and collect words for keywords
        all_hashtags = []
        all_words = []
        total_content_length = 0
        content_count = 0
        for post in posts:
            content = post.get('content', '')
            if content:
                hashtags = extract_hashtags(content)
                all_hashtags.extend(hashtags)
                total_content_length += len(content)
                content_count += 1
                # Extract words for keywords (exclude hashtags, mentions, short words)
                words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
                # Filter common stop words
                stop_words = {'this', 'that', 'with', 'from', 'your', 'have', 'been',
                             'will', 'would', 'could', 'should', 'their', 'there',
                             'they', 'them', 'then', 'than', 'what', 'when', 'where',
                             'which', 'while', 'about', 'after', 'before', 'between',
                             'into', 'through', 'during', 'each', 'very', 'just',
                             'also', 'more', 'some', 'only', 'other', 'like', 'over'}
                words = [w for w in words if w not in stop_words]
                all_words.extend(words)

        # Count and get top 20 hashtags
        hashtag_counts = Counter(all_hashtags)
        top_hashtags = [
            {'tag': tag, 'count': count}
            for tag, count in hashtag_counts.most_common(20)
        ]

        # Get top 15 keywords
        word_counts = Counter(all_words)
        keywords = [
            {'word': word, 'count': count}
            for word, count in word_counts.most_common(15)
        ]

        # Calculate content summary stats
        avg_caption_length = round(total_content_length / content_count) if content_count > 0 else 0
        
        # Get posting time heatmap (day of week and hour)
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    EXTRACT(DOW FROM timestamp) as day_of_week,
                    EXTRACT(HOUR FROM timestamp) as hour,
                    COUNT(*) as count
                FROM posts
                WHERE timestamp >= %s AND timestamp <= %s
                GROUP BY day_of_week, hour
                ORDER BY day_of_week, hour
            """, (start_dt, end_dt))
            results = cursor.fetchall()
            posting_heatmap = [
                {
                    'day': int(row[0]),  # 0=Sunday, 6=Saturday
                    'hour': int(row[1]),
                    'count': row[2]
                }
                for row in results
            ]
        
        # Get content length distribution
        with db.get_cursor() as cursor:
            cursor.execute("""
                WITH length_bins AS (
                    SELECT 
                        CASE
                            WHEN LENGTH(content) <= 50 THEN '0-50'
                            WHEN LENGTH(content) <= 100 THEN '51-100'
                            WHEN LENGTH(content) <= 200 THEN '101-200'
                            WHEN LENGTH(content) <= 500 THEN '201-500'
                            ELSE '500+'
                        END as length_bin
                    FROM posts
                    WHERE timestamp >= %s AND timestamp <= %s
                      AND content IS NOT NULL
                )
                SELECT 
                    length_bin,
                    COUNT(*) as count
                FROM length_bins
                GROUP BY length_bin
                ORDER BY 
                    CASE length_bin
                        WHEN '0-50' THEN 1
                        WHEN '51-100' THEN 2
                        WHEN '101-200' THEN 3
                        WHEN '201-500' THEN 4
                        ELSE 5
                    END
            """, (start_dt, end_dt))
            results = cursor.fetchall()
            length_distribution = [
                {'bin': row[0], 'count': row[1]}
                for row in results
            ]
        
        # Find most active day and hour from heatmap
        most_active_day = 0
        most_active_hour = 0
        max_day_count = 0
        max_hour_count = 0
        day_totals = {}
        hour_totals = {}
        for item in posting_heatmap:
            day = item['day']
            hour = item['hour']
            count = item['count']
            day_totals[day] = day_totals.get(day, 0) + count
            hour_totals[hour] = hour_totals.get(hour, 0) + count
        if day_totals:
            most_active_day = max(day_totals, key=day_totals.get)
        if hour_totals:
            most_active_hour = max(hour_totals, key=hour_totals.get)

        logger.info(
            f"Content data retrieved: {len(top_hashtags)} hashtags, "
            f"{len(posting_heatmap)} heatmap points, "
            f"date range {start_dt.date()} to {end_dt.date()}"
        )

        return {
            'hashtags': top_hashtags,
            'posting_heatmap': posting_heatmap,
            'length_distribution': length_distribution,
            'keywords': keywords,
            'total_hashtags': len(hashtag_counts),
            'avg_caption_length': avg_caption_length,
            'most_active_day': most_active_day,
            'most_active_hour': most_active_hour
        }
        
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        raise DataServiceError(f"Invalid date format: {e}")
    except DatabaseOperationError as e:
        logger.error(f"Database error getting content data: {e}")
        raise DataServiceError(f"Failed to get content data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting content data: {e}")
        raise DataServiceError(f"Unexpected error: {e}")


def get_posts_paginated(page: int = 1,
                        per_page: int = 25,
                        search: Optional[str] = None,
                        filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get paginated posts with search and filtering capabilities.
    
    Supports filtering by date range, post type, sentiment category,
    and text search on content and author fields.
    
    Args:
        page: Page number (1-indexed)
        per_page: Number of posts per page
        search: Optional search term for content/author
        filters: Optional dict with keys:
            - start_date (str): Start date in ISO format
            - end_date (str): End date in ISO format
            - media_type (str): Filter by media type
            - sentiment (str): Filter by sentiment label
            - sort_by (str): Column to sort by
            - sort_order (str): 'asc' or 'desc'
    
    Returns:
        Dict containing:
            - posts (list): List of post dictionaries
            - total (int): Total number of matching posts
            - page (int): Current page number
            - per_page (int): Posts per page
            - total_pages (int): Total number of pages
    
    Raises:
        DataServiceError: If the query fails
        
    Validates: Requirements 7.1
    """
    try:
        filters = filters or {}
        
        # Parse dates if provided
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = _parse_end_date(end_date)
        
        # Build WHERE clause conditions
        conditions = []
        params = []
        
        if start_dt:
            conditions.append("p.timestamp >= %s")
            params.append(start_dt)
        
        if end_dt:
            conditions.append("p.timestamp <= %s")
            params.append(end_dt)
        
        if filters.get('media_type'):
            conditions.append("p.media_type = %s")
            params.append(filters['media_type'])
        
        if filters.get('sentiment'):
            conditions.append("s.label = %s")
            params.append(filters['sentiment'])
        
        if search:
            conditions.append("(p.content ILIKE %s OR p.author ILIKE %s)")
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Determine sort column and order
        sort_by = filters.get('sort_by', 'timestamp')
        sort_order = filters.get('sort_order', 'desc').upper()
        
        # Validate sort order
        if sort_order not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        # Map sort column to actual column name
        sort_column_map = {
            'timestamp': 'p.timestamp',
            'author': 'p.author',
            'likes': 'p.likes',
            'comments': 'p.comments_count',
            'sentiment': 's.score'
        }
        sort_column = sort_column_map.get(sort_by, 'p.timestamp')
        
        db = get_db_connection()
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*)
            FROM posts p
            LEFT JOIN sentiments s ON p.id = s.post_id
            WHERE {where_clause}
        """
        
        with db.get_cursor() as cursor:
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
        
        # Calculate pagination
        total_pages = (total + per_page - 1) // per_page  # Ceiling division
        offset = (page - 1) * per_page
        
        # Get paginated posts
        query = f"""
            SELECT 
                p.id, p.post_id, p.platform, p.author, p.content,
                p.timestamp, p.likes, p.comments_count, p.shares,
                p.url, p.media_type,
                s.score as sentiment_score, s.label as sentiment_label
            FROM posts p
            LEFT JOIN sentiments s ON p.id = s.post_id
            WHERE {where_clause}
            ORDER BY {sort_column} {sort_order}
            LIMIT %s OFFSET %s
        """
        
        params.extend([per_page, offset])
        
        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            posts = [dict(zip(columns, row)) for row in results]
            
            # Convert datetime objects to ISO strings
            for post in posts:
                if post.get('timestamp'):
                    post['timestamp'] = post['timestamp'].isoformat()
        
        logger.info(
            f"Posts paginated: page {page}/{total_pages}, "
            f"{len(posts)} posts, total {total}"
        )
        
        return {
            'posts': posts,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }
        
    except ValueError as e:
        logger.error(f"Invalid parameter: {e}")
        raise DataServiceError(f"Invalid parameter: {e}")
    except DatabaseOperationError as e:
        logger.error(f"Database error getting paginated posts: {e}")
        raise DataServiceError(f"Failed to get paginated posts: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting paginated posts: {e}")
        raise DataServiceError(f"Unexpected error: {e}")


def get_post_comments(post_id_str: str) -> List[Dict[str, Any]]:
    """
    Get comments for a specific post.
    
    Args:
        post_id_str: The string ID of the post (e.g., from platform)
        
    Returns:
        List of comment dictionaries
        
    Raises:
        DataServiceError: If retrieval fails
    """
    try:
        # First get the post to find its DB ID
        post = get_post_by_post_id(post_id_str)
        if not post:
            return []
            
        comments = get_comments_by_post_id(post['id'])
        
        # Convert timestamps
        for comment in comments:
            if comment.get('timestamp'):
                comment['timestamp'] = comment['timestamp'].isoformat()
        
        return comments
        
    except DatabaseOperationError as e:
        logger.error(f"Database error getting comments for post {post_id_str}: {e}")
        raise DataServiceError(f"Failed to get comments: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting comments for post {post_id_str}: {e}")
        raise DataServiceError(f"Unexpected error: {e}")

