"""
Test script for new database query functions with sample data.

This script:
1. Inserts sample data into the database
2. Tests all the new query functions
3. Cleans up the test data
"""

import sys
from datetime import datetime, timedelta
from database.db_operations import (
    insert_post,
    insert_sentiment,
    get_posts_with_sentiment,
    get_sentiment_distribution,
    get_top_posts_by_engagement,
    get_hashtag_frequency,
    get_posting_time_heatmap,
    search_posts,
    DatabaseOperationError
)


def insert_sample_data():
    """Insert sample data for testing."""
    print("\n=== Inserting Sample Data ===")
    
    sample_posts = [
        {
            'post_id': 'test_post_1',
            'platform': 'instagram',
            'author': 'test_user_1',
            'content': 'Amazing sunset today! #sunset #photography #nature',
            'timestamp': datetime.now() - timedelta(days=1, hours=18),
            'likes': 150,
            'comments_count': 25,
            'shares': 10,
            'sentiment': {'score': 0.8, 'label': 'positive'}
        },
        {
            'post_id': 'test_post_2',
            'platform': 'instagram',
            'author': 'test_user_2',
            'content': 'Feeling down today... #sad #mood',
            'timestamp': datetime.now() - timedelta(days=2, hours=14),
            'likes': 50,
            'comments_count': 15,
            'shares': 2,
            'sentiment': {'score': -0.6, 'label': 'negative'}
        },
        {
            'post_id': 'test_post_3',
            'platform': 'instagram',
            'author': 'test_user_1',
            'content': 'Just another day at work #work #office #monday',
            'timestamp': datetime.now() - timedelta(days=3, hours=9),
            'likes': 75,
            'comments_count': 8,
            'shares': 3,
            'sentiment': {'score': 0.0, 'label': 'neutral'}
        },
        {
            'post_id': 'test_post_4',
            'platform': 'instagram',
            'author': 'test_user_3',
            'content': 'Best vacation ever! #travel #beach #vacation #summer',
            'timestamp': datetime.now() - timedelta(days=5, hours=12),
            'likes': 300,
            'comments_count': 45,
            'shares': 20,
            'sentiment': {'score': 0.9, 'label': 'positive'}
        },
        {
            'post_id': 'test_post_5',
            'platform': 'instagram',
            'author': 'test_user_2',
            'content': 'New recipe for dinner #food #cooking #recipe',
            'timestamp': datetime.now() - timedelta(days=7, hours=19),
            'likes': 120,
            'comments_count': 30,
            'shares': 15,
            'sentiment': {'score': 0.3, 'label': 'positive'}
        },
    ]
    
    inserted_ids = []
    
    try:
        for post_data in sample_posts:
            # Insert post
            post_id = insert_post(
                post_id=post_data['post_id'],
                platform=post_data['platform'],
                author=post_data['author'],
                content=post_data['content'],
                timestamp=post_data['timestamp'],
                likes=post_data['likes'],
                comments_count=post_data['comments_count'],
                shares=post_data['shares']
            )
            inserted_ids.append(post_id)
            
            # Insert sentiment
            sentiment = post_data['sentiment']
            insert_sentiment(
                post_id=post_id,
                score=sentiment['score'],
                label=sentiment['label'],
                confidence=0.85,
                compound=sentiment['score'],
                positive=max(0, sentiment['score']),
                neutral=0.0 if sentiment['score'] != 0 else 1.0,
                negative=abs(min(0, sentiment['score'])),
                model='vader'
            )
        
        print(f"✓ Inserted {len(inserted_ids)} sample posts with sentiment data")
        return inserted_ids
        
    except Exception as e:
        print(f"✗ Error inserting sample data: {e}")
        import traceback
        traceback.print_exc()
        return []


def cleanup_sample_data(post_ids):
    """Clean up sample data."""
    print("\n=== Cleaning Up Sample Data ===")
    try:
        from database.db_connection import get_db_connection
        db = get_db_connection()
        
        with db.get_cursor(commit=True) as cursor:
            # Delete test posts (sentiments will be deleted via CASCADE)
            cursor.execute("""
                DELETE FROM posts 
                WHERE post_id LIKE 'test_post_%'
            """)
            deleted = cursor.rowcount
            print(f"✓ Deleted {deleted} test posts")
        
        return True
    except Exception as e:
        print(f"✗ Error cleaning up: {e}")
        return False


def test_with_data():
    """Run tests with sample data."""
    print("=" * 70)
    print("Testing Database Query Functions with Sample Data")
    print("=" * 70)
    
    # Insert sample data
    post_ids = insert_sample_data()
    if not post_ids:
        print("\n✗ Failed to insert sample data. Aborting tests.")
        return False
    
    try:
        # Test 1: get_posts_with_sentiment
        print("\n=== Test 1: get_posts_with_sentiment ===")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        results = get_posts_with_sentiment(start_date, end_date)
        print(f"✓ Retrieved {len(results)} posts with sentiment")
        if results:
            for post in results[:3]:
                print(f"  - {post['author']}: {post['label']} ({post['score']})")
        
        # Test 2: get_sentiment_distribution
        print("\n=== Test 2: get_sentiment_distribution ===")
        distribution = get_sentiment_distribution(start_date, end_date)
        print(f"✓ Sentiment distribution: {distribution}")
        
        # Test 3: get_top_posts_by_engagement
        print("\n=== Test 3: get_top_posts_by_engagement ===")
        top_posts = get_top_posts_by_engagement(start_date, end_date, limit=3)
        print(f"✓ Top {len(top_posts)} posts by engagement:")
        for i, post in enumerate(top_posts, 1):
            engagement = post['total_engagement']
            print(f"  {i}. {post['author']}: {engagement} total engagement")
        
        # Test 4: get_hashtag_frequency
        print("\n=== Test 4: get_hashtag_frequency ===")
        hashtags = get_hashtag_frequency(start_date, end_date, limit=10)
        print(f"✓ Top {len(hashtags)} hashtags:")
        for i, item in enumerate(hashtags, 1):
            print(f"  {i}. #{item['hashtag']}: {item['count']} occurrences")
        
        # Test 5: get_posting_time_heatmap
        print("\n=== Test 5: get_posting_time_heatmap ===")
        heatmap = get_posting_time_heatmap(start_date, end_date)
        print(f"✓ Posting time heatmap: {len(heatmap)} time slots")
        day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        for item in heatmap[:5]:
            day = day_names[item['day_of_week']]
            print(f"  - {day} {item['hour']:02d}:00: {item['count']} posts")
        
        # Test 6: search_posts - basic search
        print("\n=== Test 6: search_posts (basic) ===")
        results = search_posts(page=1, per_page=10)
        print(f"✓ Found {results['total']} total posts")
        print(f"  Page {results['page']}/{results['total_pages']}")
        
        # Test 7: search_posts - with search term
        print("\n=== Test 7: search_posts (with search term) ===")
        results = search_posts(search_term='vacation', page=1, per_page=10)
        print(f"✓ Found {results['total']} posts matching 'vacation'")
        if results['posts']:
            for post in results['posts']:
                print(f"  - {post['author']}: {post['content'][:50]}...")
        
        # Test 8: search_posts - with filters
        print("\n=== Test 8: search_posts (with filters) ===")
        filters = {
            'start_date': start_date,
            'end_date': end_date,
            'sentiment_label': 'positive',
            'sort_by': 'likes',
            'sort_order': 'desc'
        }
        results = search_posts(filters=filters, page=1, per_page=10)
        print(f"✓ Found {results['total']} positive posts")
        if results['posts']:
            for post in results['posts'][:3]:
                print(f"  - {post['author']}: {post['likes']} likes, {post['label']} sentiment")
        
        # Test 9: search_posts - pagination
        print("\n=== Test 9: search_posts (pagination) ===")
        results_p1 = search_posts(page=1, per_page=2)
        results_p2 = search_posts(page=2, per_page=2)
        print(f"✓ Page 1: {len(results_p1['posts'])} posts")
        print(f"✓ Page 2: {len(results_p2['posts'])} posts")
        print(f"  Total pages: {results_p1['total_pages']}")
        
        print("\n" + "=" * 70)
        print("✓ All tests passed successfully!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        cleanup_sample_data(post_ids)


if __name__ == "__main__":
    success = test_with_data()
    sys.exit(0 if success else 1)
