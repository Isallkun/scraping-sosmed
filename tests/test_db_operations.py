"""
Unit tests for database operations module.

Tests cover:
- Insert operations with upsert logic
- Foreign key handling
- Query methods for reports
- Parameterized queries
- Error handling
- Data retention operations
"""

import os
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta
from psycopg2 import DatabaseError, IntegrityError

from database.db_operations import (
    insert_post,
    insert_sentiment,
    insert_execution_log,
    get_post_by_post_id,
    get_post_by_id,
    get_posts_by_date_range,
    get_sentiment_by_post_id,
    get_posts_with_sentiment,
    get_sentiment_distribution,
    get_top_posts_by_engagement,
    get_execution_logs,
    get_daily_post_counts,
    delete_old_posts,
    delete_old_execution_logs,
    DatabaseOperationError
)


@pytest.fixture
def mock_db_connection():
    """Fixture for mocked database connection"""
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    
    # Setup context manager for get_cursor
    mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
    mock_db.get_cursor.return_value.__exit__.return_value = False
    
    with patch('database.db_operations.get_db_connection', return_value=mock_db):
        yield mock_db, mock_cursor


class TestInsertPost:
    """Test insert_post function with upsert logic"""
    
    def test_insert_new_post_success(self, mock_db_connection):
        """Test inserting a new post successfully"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (1,)  # Return ID
        
        post_id = "post123"
        platform = "instagram"
        author = "testuser"
        content = "Test post content"
        timestamp = datetime.now()
        
        result = insert_post(
            post_id=post_id,
            platform=platform,
            author=author,
            content=content,
            timestamp=timestamp,
            likes=100,
            comments_count=10,
            shares=5
        )
        
        assert result == 1
        mock_cursor.execute.assert_called_once()
        
        # Verify parameterized query was used
        call_args = mock_cursor.execute.call_args
        assert post_id in call_args[0][1]
        assert platform in call_args[0][1]
        assert author in call_args[0][1]
    
    def test_insert_post_with_optional_fields(self, mock_db_connection):
        """Test inserting post with all optional fields"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (2,)
        
        result = insert_post(
            post_id="post456",
            platform="twitter",
            author="user2",
            content="Tweet content",
            timestamp=datetime.now(),
            likes=50,
            comments_count=5,
            shares=2,
            url="https://twitter.com/user2/status/123",
            author_id="user2_id",
            media_type="image",
            hashtags=["test", "python"],
            raw_data={"extra": "data"}
        )
        
        assert result == 2
        mock_cursor.execute.assert_called_once()
    
    def test_insert_post_upsert_on_conflict(self, mock_db_connection):
        """Test upsert behavior when post_id already exists"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (1,)  # Same ID returned
        
        # Insert same post_id twice
        post_id = "duplicate_post"
        
        result = insert_post(
            post_id=post_id,
            platform="instagram",
            author="user",
            content="Original content",
            timestamp=datetime.now()
        )
        
        assert result == 1
        
        # Verify ON CONFLICT UPDATE is in the query
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        assert "ON CONFLICT" in query
        assert "DO UPDATE SET" in query
    
    def test_insert_post_database_error(self, mock_db_connection):
        """Test handling of database errors"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = DatabaseError("Connection lost")
        
        with pytest.raises(DatabaseOperationError) as exc_info:
            insert_post(
                post_id="post789",
                platform="facebook",
                author="user3",
                content="Content",
                timestamp=datetime.now()
            )
        
        assert "Failed to insert post" in str(exc_info.value)


class TestInsertSentiment:
    """Test insert_sentiment function with foreign key handling"""
    
    def test_insert_sentiment_success(self, mock_db_connection):
        """Test inserting sentiment successfully"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (1,)
        
        result = insert_sentiment(
            post_id=1,
            score=0.75,
            label="positive",
            confidence=0.85,
            compound=0.75,
            positive=0.8,
            neutral=0.15,
            negative=0.05,
            model="vader"
        )
        
        assert result == 1
        mock_cursor.execute.assert_called_once()
        
        # Verify parameterized query
        call_args = mock_cursor.execute.call_args
        assert 1 in call_args[0][1]  # post_id
        assert 0.75 in call_args[0][1]  # score
        assert "positive" in call_args[0][1]  # label
    
    def test_insert_sentiment_foreign_key_violation(self, mock_db_connection):
        """Test handling of foreign key constraint violation"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = IntegrityError(
            "foreign key constraint \"sentiments_post_id_fkey\" violated"
        )
        
        with pytest.raises(DatabaseOperationError) as exc_info:
            insert_sentiment(
                post_id=999,  # Non-existent post
                score=0.5,
                label="neutral",
                confidence=0.6,
                compound=0.0,
                positive=0.3,
                neutral=0.4,
                negative=0.3
            )
        
        assert "does not exist" in str(exc_info.value)
    
    def test_insert_sentiment_with_textblob_model(self, mock_db_connection):
        """Test inserting sentiment with textblob model"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (2,)
        
        result = insert_sentiment(
            post_id=1,
            score=-0.3,
            label="negative",
            confidence=0.7,
            compound=-0.3,
            positive=0.2,
            neutral=0.3,
            negative=0.5,
            model="textblob"
        )
        
        assert result == 2
        call_args = mock_cursor.execute.call_args
        assert "textblob" in call_args[0][1]


class TestInsertExecutionLog:
    """Test insert_execution_log function"""
    
    def test_insert_execution_log_success(self, mock_db_connection):
        """Test inserting execution log successfully"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (1,)
        
        result = insert_execution_log(
            workflow_id="wf_123",
            workflow_name="daily_scraping",
            status="success",
            duration_ms=15000,
            metadata={"posts_scraped": 50}
        )
        
        assert result == 1
        mock_cursor.execute.assert_called_once()
        
        call_args = mock_cursor.execute.call_args
        assert "wf_123" in call_args[0][1]
        assert "daily_scraping" in call_args[0][1]
        assert "success" in call_args[0][1]
    
    def test_insert_execution_log_with_error(self, mock_db_connection):
        """Test inserting execution log with error details"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (2,)
        
        result = insert_execution_log(
            workflow_id="wf_456",
            workflow_name="webhook_scraping",
            status="failed",
            duration_ms=5000,
            error_message="Scraper authentication failed",
            error_stack="Traceback...",
            metadata={"target_url": "https://example.com"}
        )
        
        assert result == 2
        call_args = mock_cursor.execute.call_args
        assert "failed" in call_args[0][1]
        assert "Scraper authentication failed" in call_args[0][1]


class TestQueryMethods:
    """Test query methods for retrieving data"""
    
    def test_get_post_by_post_id_found(self, mock_db_connection):
        """Test retrieving post by post_id when it exists"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('id',), ('post_id',), ('platform',), ('author',), ('content',)
        ]
        mock_cursor.fetchone.return_value = (1, 'post123', 'instagram', 'user', 'content')
        
        result = get_post_by_post_id('post123')
        
        assert result is not None
        assert result['post_id'] == 'post123'
        assert result['platform'] == 'instagram'
        
        call_args = mock_cursor.execute.call_args
        assert 'post123' in call_args[0][1]
    
    def test_get_post_by_post_id_not_found(self, mock_db_connection):
        """Test retrieving post by post_id when it doesn't exist"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None
        
        result = get_post_by_post_id('nonexistent')
        
        assert result is None
    
    def test_get_post_by_id(self, mock_db_connection):
        """Test retrieving post by database ID"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('id',), ('post_id',), ('platform',)
        ]
        mock_cursor.fetchone.return_value = (1, 'post123', 'twitter')
        
        result = get_post_by_id(1)
        
        assert result is not None
        assert result['id'] == 1
        assert result['post_id'] == 'post123'
    
    def test_get_posts_by_date_range(self, mock_db_connection):
        """Test retrieving posts by date range"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('id',), ('post_id',), ('timestamp',)
        ]
        mock_cursor.fetchall.return_value = [
            (1, 'post1', datetime.now()),
            (2, 'post2', datetime.now())
        ]
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        result = get_posts_by_date_range(start_date, end_date)
        
        assert len(result) == 2
        assert result[0]['post_id'] == 'post1'
        
        call_args = mock_cursor.execute.call_args
        assert start_date in call_args[0][1]
        assert end_date in call_args[0][1]
    
    def test_get_posts_by_date_range_with_platform_filter(self, mock_db_connection):
        """Test retrieving posts by date range with platform filter"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.description = [('id',), ('post_id',), ('platform',)]
        mock_cursor.fetchall.return_value = [
            (1, 'post1', 'instagram')
        ]
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        result = get_posts_by_date_range(start_date, end_date, platform='instagram')
        
        assert len(result) == 1
        call_args = mock_cursor.execute.call_args
        assert 'instagram' in call_args[0][1]
    
    def test_get_sentiment_by_post_id(self, mock_db_connection):
        """Test retrieving sentiment by post ID"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('id',), ('post_id',), ('score',), ('label',)
        ]
        mock_cursor.fetchone.return_value = (1, 1, 0.75, 'positive')
        
        result = get_sentiment_by_post_id(1)
        
        assert result is not None
        assert result['score'] == 0.75
        assert result['label'] == 'positive'
    
    def test_get_posts_with_sentiment(self, mock_db_connection):
        """Test retrieving posts with sentiment data (JOIN query)"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('id',), ('post_id',), ('content',), ('score',), ('label',)
        ]
        mock_cursor.fetchall.return_value = [
            (1, 'post1', 'content1', 0.8, 'positive'),
            (2, 'post2', 'content2', -0.3, 'negative')
        ]
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        result = get_posts_with_sentiment(start_date, end_date)
        
        assert len(result) == 2
        assert result[0]['label'] == 'positive'
        assert result[1]['label'] == 'negative'
        
        # Verify JOIN is in query
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        assert 'JOIN' in query


class TestReportQueries:
    """Test report and analytics query methods"""
    
    def test_get_sentiment_distribution(self, mock_db_connection):
        """Test getting sentiment distribution"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = [
            ('positive', 150),
            ('neutral', 75),
            ('negative', 25)
        ]
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        result = get_sentiment_distribution(start_date, end_date)
        
        assert result['positive'] == 150
        assert result['neutral'] == 75
        assert result['negative'] == 25
    
    def test_get_sentiment_distribution_missing_labels(self, mock_db_connection):
        """Test sentiment distribution fills in missing labels with 0"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = [
            ('positive', 100)
            # neutral and negative missing
        ]
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        result = get_sentiment_distribution(start_date, end_date)
        
        assert result['positive'] == 100
        assert result['neutral'] == 0
        assert result['negative'] == 0
    
    def test_get_top_posts_by_engagement(self, mock_db_connection):
        """Test getting top posts by engagement"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('id',), ('post_id',), ('likes',), ('comments_count',), 
            ('shares',), ('total_engagement',)
        ]
        mock_cursor.fetchall.return_value = [
            (1, 'post1', 100, 50, 25, 175),
            (2, 'post2', 80, 40, 20, 140)
        ]
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        result = get_top_posts_by_engagement(start_date, end_date, limit=10)
        
        assert len(result) == 2
        assert result[0]['total_engagement'] == 175
        
        # Verify ORDER BY and LIMIT in query
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        assert 'ORDER BY' in query
        assert 'LIMIT' in query
    
    def test_get_execution_logs_no_filters(self, mock_db_connection):
        """Test getting execution logs without filters"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('id',), ('workflow_name',), ('status',)
        ]
        mock_cursor.fetchall.return_value = [
            (1, 'daily_scraping', 'success'),
            (2, 'webhook_scraping', 'failed')
        ]
        
        result = get_execution_logs(limit=100)
        
        assert len(result) == 2
    
    def test_get_execution_logs_with_filters(self, mock_db_connection):
        """Test getting execution logs with workflow and status filters"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('id',), ('workflow_name',), ('status',)
        ]
        mock_cursor.fetchall.return_value = [
            (1, 'daily_scraping', 'failed')
        ]
        
        result = get_execution_logs(
            workflow_name='daily_scraping',
            status='failed',
            limit=50
        )
        
        assert len(result) == 1
        
        call_args = mock_cursor.execute.call_args
        assert 'daily_scraping' in call_args[0][1]
        assert 'failed' in call_args[0][1]
    
    def test_get_daily_post_counts(self, mock_db_connection):
        """Test getting daily post counts"""
        mock_db, mock_cursor = mock_db_connection
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        mock_cursor.fetchall.return_value = [
            (yesterday, 50),
            (today, 75)
        ]
        
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        result = get_daily_post_counts(start_date, end_date)
        
        assert len(result) == 2
        assert result[0][1] == 50  # Count for yesterday
        assert result[1][1] == 75  # Count for today
        
        # Verify GROUP BY in query
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        assert 'GROUP BY' in query


class TestDataRetention:
    """Test data retention and cleanup operations"""
    
    def test_delete_old_posts(self, mock_db_connection):
        """Test deleting old posts"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 25  # 25 posts deleted
        
        result = delete_old_posts(days=90)
        
        assert result == 25
        
        # Verify DELETE query with date parameter
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        assert 'DELETE FROM posts' in query
        assert 'timestamp <' in query
    
    def test_delete_old_posts_custom_retention(self, mock_db_connection):
        """Test deleting old posts with custom retention period"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 10
        
        result = delete_old_posts(days=30)
        
        assert result == 10
    
    def test_delete_old_execution_logs(self, mock_db_connection):
        """Test deleting old execution logs"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 100
        
        result = delete_old_execution_logs(days=30)
        
        assert result == 100
        
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        assert 'DELETE FROM execution_logs' in query
        assert 'executed_at <' in query
    
    def test_delete_old_posts_database_error(self, mock_db_connection):
        """Test handling database error during deletion"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = DatabaseError("Delete failed")
        
        with pytest.raises(DatabaseOperationError) as exc_info:
            delete_old_posts(days=90)
        
        assert "Failed to delete old posts" in str(exc_info.value)


class TestErrorHandling:
    """Test error handling across all operations"""
    
    def test_query_database_error(self, mock_db_connection):
        """Test handling of database errors in query operations"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = DatabaseError("Query failed")
        
        with pytest.raises(DatabaseOperationError):
            get_post_by_post_id('post123')
    
    def test_parameterized_queries_prevent_injection(self, mock_db_connection):
        """Test that parameterized queries are used (SQL injection prevention)"""
        mock_db, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None
        
        # Try to inject SQL
        malicious_input = "'; DROP TABLE posts; --"
        
        get_post_by_post_id(malicious_input)
        
        # Verify parameterized query was used (not string concatenation)
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        # Query should use %s placeholder
        assert '%s' in query
        # Malicious input should be in params tuple, not in query string
        assert malicious_input in params
        assert 'DROP TABLE' not in query
