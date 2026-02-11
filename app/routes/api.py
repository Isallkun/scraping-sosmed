"""
API Routes Module

This module defines RESTful API endpoints for the Flask Analytics Dashboard.
All endpoints return JSON responses and support CORS for cross-origin requests.

Endpoints:
- GET /api/summary: Overall statistics
- GET /api/sentiment: Sentiment distribution and trends
- GET /api/engagement: Engagement metrics and top posts
- GET /api/content: Content analysis (hashtags, posting patterns)
- GET /api/posts: Paginated posts with search and filters
- GET /api/export: CSV export of filtered posts

Validates Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.7, 7.5
"""

import logging
import csv
import io
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, current_app
from app import cache
from app.services.data_service import (
    get_summary_stats,
    get_sentiment_data,
    get_engagement_data,
    get_content_data,
    get_posts_paginated,
    get_post_comments,
    DataServiceError
)
from app.services.import_service import process_import_file, ImportServiceError

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


def validate_date_parameter(date_str: str, param_name: str) -> bool:
    """
    Validate date parameter format.
    
    Args:
        date_str: Date string to validate
        param_name: Parameter name for error messages
        
    Returns:
        bool: True if valid or None, raises ValueError if invalid
        
    Raises:
        ValueError: If date format is invalid
    """
    if date_str is None:
        return True
    
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        raise ValueError(
            f"Invalid date format for {param_name}. "
            f"Expected ISO format (YYYY-MM-DD), got: {date_str}"
        )


def validate_pagination_parameters(page: int, per_page: int) -> bool:
    """
    Validate pagination parameters.
    
    Args:
        page: Page number
        per_page: Items per page
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If parameters are invalid
    """
    if page < 1:
        raise ValueError(f"Page number must be >= 1, got: {page}")
    
    if per_page < 1:
        raise ValueError(f"Per page must be >= 1, got: {per_page}")
    
    if per_page > 100:
        raise ValueError(f"Per page must be <= 100, got: {per_page}")
    
    return True


def create_error_response(message: str, status_code: int = 400):
    """
    Create standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        
    Returns:
        tuple: (JSON response, status code)
    """
    return jsonify({
        'error': message,
        'status': status_code,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), status_code


@api_bp.route('/summary')
@cache.cached(timeout=300)
def get_summary():
    """
    Get overall statistics for the dashboard.
    
    Returns:
        JSON response with:
            - total_posts: Total number of posts
            - total_comments: Total number of comments
            - avg_sentiment: Average sentiment score
            - last_execution: Last scraping execution timestamp
            - post_type_distribution: Count by media type
    
    Status Codes:
        200: Success
        500: Internal server error
        
    Validates: Requirement 8.1
    """
    try:
        logger.info("GET /api/summary")
        data = get_summary_stats()
        return jsonify(data), 200
        
    except DataServiceError as e:
        logger.error(f"Error in /api/summary: {e}")
        return create_error_response(
            "Failed to retrieve summary statistics",
            500
        )
    except Exception as e:
        logger.error(f"Unexpected error in /api/summary: {e}", exc_info=True)
        return create_error_response(
            "Internal server error",
            500
        )


@api_bp.route('/sentiment')
@cache.cached(timeout=300, query_string=True)
def get_sentiment():
    """
    Get sentiment distribution and trends.
    
    Query Parameters:
        start_date (optional): Start date in ISO format (YYYY-MM-DD)
        end_date (optional): End date in ISO format (YYYY-MM-DD)
    
    Returns:
        JSON response with:
            - distribution: Sentiment counts and percentages by category
            - trends: Daily sentiment scores over time
            - gauge: Average sentiment score
    
    Status Codes:
        200: Success
        400: Invalid parameters
        500: Internal server error
        
    Validates: Requirement 8.2, 8.6
    """
    try:
        # Get and validate query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        validate_date_parameter(start_date, 'start_date')
        validate_date_parameter(end_date, 'end_date')
        
        logger.info(f"GET /api/sentiment?start_date={start_date}&end_date={end_date}")
        
        data = get_sentiment_data(start_date, end_date)
        return jsonify(data), 200
        
    except ValueError as e:
        logger.warning(f"Invalid parameters in /api/sentiment: {e}")
        return create_error_response(str(e), 400)
    except DataServiceError as e:
        logger.error(f"Error in /api/sentiment: {e}")
        return create_error_response(
            "Failed to retrieve sentiment data",
            500
        )
    except Exception as e:
        logger.error(f"Unexpected error in /api/sentiment: {e}", exc_info=True)
        return create_error_response(
            "Internal server error",
            500
        )


@api_bp.route('/engagement')
@cache.cached(timeout=300, query_string=True)
def get_engagement():
    """
    Get engagement metrics and top posts.
    
    Query Parameters:
        start_date (optional): Start date in ISO format (YYYY-MM-DD)
        end_date (optional): End date in ISO format (YYYY-MM-DD)
    
    Returns:
        JSON response with:
            - top_posts: Top 10 posts by engagement
            - trends: Daily engagement rates over time
            - type_distribution: Count by post type
    
    Status Codes:
        200: Success
        400: Invalid parameters
        500: Internal server error
        
    Validates: Requirement 8.3, 8.6
    """
    try:
        # Get and validate query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        validate_date_parameter(start_date, 'start_date')
        validate_date_parameter(end_date, 'end_date')
        
        logger.info(f"GET /api/engagement?start_date={start_date}&end_date={end_date}")
        
        data = get_engagement_data(start_date, end_date)
        return jsonify(data), 200
        
    except ValueError as e:
        logger.warning(f"Invalid parameters in /api/engagement: {e}")
        return create_error_response(str(e), 400)
    except DataServiceError as e:
        logger.error(f"Error in /api/engagement: {e}")
        return create_error_response(
            "Failed to retrieve engagement data",
            500
        )
    except Exception as e:
        logger.error(f"Unexpected error in /api/engagement: {e}", exc_info=True)
        return create_error_response(
            "Internal server error",
            500
        )


@api_bp.route('/content')
@cache.cached(timeout=300, query_string=True)
def get_content():
    """
    Get content analysis data.
    
    Query Parameters:
        start_date (optional): Start date in ISO format (YYYY-MM-DD)
        end_date (optional): End date in ISO format (YYYY-MM-DD)
    
    Returns:
        JSON response with:
            - hashtags: Top 20 hashtags by frequency
            - posting_heatmap: Posts by day of week and hour
            - length_distribution: Content length distribution
    
    Status Codes:
        200: Success
        400: Invalid parameters
        500: Internal server error
        
    Validates: Requirement 8.4, 8.6
    """
    try:
        # Get and validate query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        validate_date_parameter(start_date, 'start_date')
        validate_date_parameter(end_date, 'end_date')
        
        logger.info(f"GET /api/content?start_date={start_date}&end_date={end_date}")
        
        data = get_content_data(start_date, end_date)
        return jsonify(data), 200
        
    except ValueError as e:
        logger.warning(f"Invalid parameters in /api/content: {e}")
        return create_error_response(str(e), 400)
    except DataServiceError as e:
        logger.error(f"Error in /api/content: {e}")
        return create_error_response(
            "Failed to retrieve content data",
            500
        )
    except Exception as e:
        logger.error(f"Unexpected error in /api/content: {e}", exc_info=True)
        return create_error_response(
            "Internal server error",
            500
        )


@api_bp.route('/posts')
@cache.cached(timeout=300, query_string=True)
def get_posts():
    """
    Get paginated posts with search and filtering.
    
    Query Parameters:
        page (optional): Page number (default: 1)
        per_page (optional): Items per page (default: 25, max: 100)
        search (optional): Search term for content/author
        start_date (optional): Start date filter (YYYY-MM-DD)
        end_date (optional): End date filter (YYYY-MM-DD)
        media_type (optional): Filter by media type
        sentiment (optional): Filter by sentiment label
        sort_by (optional): Column to sort by (default: timestamp)
        sort_order (optional): Sort order 'asc' or 'desc' (default: desc)
    
    Returns:
        JSON response with:
            - posts: List of post objects
            - total: Total number of matching posts
            - page: Current page number
            - per_page: Items per page
            - total_pages: Total number of pages
    
    Status Codes:
        200: Success
        400: Invalid parameters
        500: Internal server error
        
    Validates: Requirement 8.5, 8.6, 8.8
    """
    try:
        # Get and validate pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        
        validate_pagination_parameters(page, per_page)
        
        # Get search parameter
        search = request.args.get('search')
        
        # Get and validate filter parameters
        filters = {}
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            validate_date_parameter(start_date, 'start_date')
            filters['start_date'] = start_date
        
        if end_date:
            validate_date_parameter(end_date, 'end_date')
            filters['end_date'] = end_date
        
        # Optional filters
        if request.args.get('media_type'):
            filters['media_type'] = request.args.get('media_type')
        
        if request.args.get('sentiment'):
            filters['sentiment'] = request.args.get('sentiment')
        
        if request.args.get('sort_by'):
            filters['sort_by'] = request.args.get('sort_by')
        
        if request.args.get('sort_order'):
            sort_order = request.args.get('sort_order').lower()
            if sort_order not in ['asc', 'desc']:
                raise ValueError(f"Invalid sort_order. Must be 'asc' or 'desc', got: {sort_order}")
            filters['sort_order'] = sort_order
        
        logger.info(
            f"GET /api/posts?page={page}&per_page={per_page}"
            f"&search={search}&filters={filters}"
        )
        
        data = get_posts_paginated(page, per_page, search, filters)
        return jsonify(data), 200
        
    except ValueError as e:
        logger.warning(f"Invalid parameters in /api/posts: {e}")
        return create_error_response(str(e), 400)
    except DataServiceError as e:
        logger.error(f"Error in /api/posts: {e}")
        return create_error_response(
            "Failed to retrieve posts",
            500
        )
    except Exception as e:
        logger.error(f"Unexpected error in /api/posts: {e}", exc_info=True)
        return create_error_response(
            "Internal server error",
            500
        )


@api_bp.route('/export')
def export_posts():
    """
    Export filtered posts to CSV file.
    
    Query Parameters:
        search (optional): Search term for content/author
        start_date (optional): Start date filter (YYYY-MM-DD)
        end_date (optional): End date filter (YYYY-MM-DD)
        media_type (optional): Filter by media type
        sentiment (optional): Filter by sentiment label
    
    Returns:
        CSV file download with filtered posts
    
    Status Codes:
        200: Success (CSV file)
        400: Invalid parameters
        500: Internal server error
        
    Validates: Requirement 7.5
    """
    try:
        # Get search parameter
        search = request.args.get('search')
        
        # Get and validate filter parameters
        filters = {}
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            validate_date_parameter(start_date, 'start_date')
            filters['start_date'] = start_date
        
        if end_date:
            validate_date_parameter(end_date, 'end_date')
            filters['end_date'] = end_date
        
        # Optional filters
        if request.args.get('media_type'):
            filters['media_type'] = request.args.get('media_type')
        
        if request.args.get('sentiment'):
            filters['sentiment'] = request.args.get('sentiment')
        
        logger.info(f"GET /api/export?search={search}&filters={filters}")
        
        # Get all matching posts (no pagination for export)
        # Use a large per_page value to get all results
        data = get_posts_paginated(1, 10000, search, filters)
        posts = data['posts']
        
        # Create CSV in memory
        output = io.StringIO()
        
        if posts:
            # Define CSV columns
            fieldnames = [
                'post_id', 'platform', 'author', 'content', 'timestamp',
                'likes', 'comments_count', 'shares', 'url', 'media_type',
                'sentiment_score', 'sentiment_label'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for post in posts:
                # Write only the fields we want in the CSV
                row = {field: post.get(field, '') for field in fieldnames}
                writer.writerow(row)
        else:
            # Empty CSV with headers
            writer = csv.writer(output)
            writer.writerow([
                'post_id', 'platform', 'author', 'content', 'timestamp',
                'likes', 'comments_count', 'shares', 'url', 'media_type',
                'sentiment_score', 'sentiment_label'
            ])
        
        # Prepare file for download
        output.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'posts_export_{timestamp}.csv'
        
        logger.info(f"Exporting {len(posts)} posts to CSV: {filename}")
        
        # Create response with CSV file
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except ValueError as e:
        logger.warning(f"Invalid parameters in /api/export: {e}")
        return create_error_response(str(e), 400)
    except DataServiceError as e:
        logger.error(f"Error in /api/export: {e}")
        return create_error_response(
            "Failed to export posts",
            500
        )
    except Exception as e:
        logger.error(f"Unexpected error in /api/export: {e}", exc_info=True)
        return create_error_response(
            "Internal server error",
            500
        )


@api_bp.route('/posts/<post_id>/comments')
def get_comments(post_id):
    """
    Get comments for a specific post.
    
    Args:
        post_id: Post ID (string)
        
    Returns:
        JSON response with list of comments
    """
    try:
        comments = get_post_comments(post_id)
        return jsonify(comments), 200
        
    except DataServiceError as e:
        logger.error(f"Error getting comments: {e}")
        return create_error_response("Failed to retrieve comments", 500)
    except Exception as e:
        logger.error(f"Unexpected error getting comments: {e}", exc_info=True)
        return create_error_response("Internal server error", 500)


@api_bp.route('/import', methods=['POST'])
def import_data():
    """
    Import posts from CSV or JSON file.
    
    Form Data:
        file: The file to upload (CSV or JSON)
        platform: The platform name (default: instagram)
        clear_existing: Whether to clear existing data before import (default: true)
    
    Returns:
        JSON response with import statistics
        
    Status Codes:
        200: Success
        400: Invalid file or format
        500: Internal server error
    """
    try:
        if 'file' not in request.files:
            return create_error_response("No file part", 400)
            
        file = request.files['file']
        
        if file.filename == '':
            return create_error_response("No selected file", 400)
            
        if not file:
            return create_error_response("Empty file", 400)

        # Determine file type from extension
        filename = file.filename.lower()
        if filename.endswith('.json'):
            file_type = 'json'
        elif filename.endswith('.csv'):
            file_type = 'csv'
        else:
            return create_error_response("Unsupported file type. Please upload .json or .csv", 400)
            
        platform = request.form.get('platform', 'instagram')
        
        # Get clear_existing parameter (default: true)
        clear_existing_str = request.form.get('clear_existing', 'true').lower()
        clear_existing = clear_existing_str in ['true', '1', 'yes']
        
        logger.info(f"POST /api/import file={filename} type={file_type} platform={platform} clear_existing={clear_existing}")
        
        result = process_import_file(file, file_type, platform, clear_existing)
        
        # Build response message
        message = 'Import completed successfully'
        if clear_existing and 'cleared' in result:
            message += f" (Cleared {result['cleared']['posts']} existing posts first)"
        
        return jsonify({
            'message': message,
            'stats': result
        }), 200
        
    except ImportServiceError as e:
        logger.error(f"Import error: {e}")
        return create_error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Unexpected error in /api/import: {e}", exc_info=True)
        return create_error_response("Internal server error during import", 500)


# Error handler for blueprint
@api_bp.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors for API routes"""
    logger.warning(f"API endpoint not found: {request.path}")
    return create_error_response("API endpoint not found", 404)


@api_bp.errorhandler(500)
def api_internal_error(error):
    """Handle 500 errors for API routes"""
    logger.error(f"Internal error in API: {error}", exc_info=True)
    return create_error_response("Internal server error", 500)
