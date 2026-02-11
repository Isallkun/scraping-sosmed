"""
Test script for new database query functions.

This script tests the newly implemented database query functions:
- get_hashtag_frequency
- get_posting_time_heatmap
- search_posts

It also verifies that the existing functions still work:
- get_posts_with_sentiment
- get_sentiment_distribution
- get_top_posts_by_engagement
"""

import sys
from datetime import datetime, timedelta
from database.db_operations import (
    get_posts_with_sentiment,
    get_sentiment_distribution,
    get_top_posts_by_engagement,
    get_hashtag_frequency,
    get_posting_time_heatmap,
    search_posts,
    DatabaseOperationError
)


def test_get_posts_with_sentiment():
    """Test get_posts_with_sentiment function."""
    print("\n=== Testing get_posts_with_sentiment ===")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        results = get_posts_with_sentiment(start_date, end_date)
        print(f"✓ Retrieved {len(results)} posts with sentiment data")
        
        if results:
            sample = results[0]
            print(f"  Sample post: {sample.get('author', 'N/A')} - {sample.get('label', 'N/A')}")
        
        return True
    except DatabaseOperationError as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_get_sentiment_distribution():
    """Test get_sentiment_distribution function."""
    print("\n=== Testing get_sentiment_distribution ===")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        results = get_sentiment_distribution(start_date, end_date)
        print(f"✓ Retrieved sentiment distribution: {results}")
        
        return True
    except DatabaseOperationError as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_get_top_posts_by_engagement():
    """Test get_top_posts_by_engagement function."""
    print("\n=== Testing get_top_posts_by_engagement ===")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        results = get_top_posts_by_engagement(start_date, end_date, limit=5)
        print(f"✓ Retrieved {len(results)} top posts by engagement")
        
        if results:
            for i, post in enumerate(results[:3], 1):
                engagement = post.get('total_engagement', 0)
                author = post.get('author', 'N/A')
                print(f"  {i}. {author}: {engagement} total engagement")
        
        return True
    except DatabaseOperationError as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_get_hashtag_frequency():
    """Test get_hashtag_frequency function."""
    print("\n=== Testing get_hashtag_frequency ===")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        results = get_hashtag_frequency(start_date, end_date, limit=10)
        print(f"✓ Retrieved {len(results)} hashtags")
        
        if results:
            for i, item in enumerate(results[:5], 1):
                print(f"  {i}. #{item['hashtag']}: {item['count']} occurrences")
        else:
            print("  No hashtags found (posts may not contain hashtags)")
        
        return True
    except DatabaseOperationError as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_get_posting_time_heatmap():
    """Test get_posting_time_heatmap function."""
    print("\n=== Testing get_posting_time_heatmap ===")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        results = get_posting_time_heatmap(start_date, end_date)
        print(f"✓ Retrieved {len(results)} time slots")
        
        if results:
            # Show a few samples
            for i, item in enumerate(results[:5], 1):
                day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                day = day_names[item['day_of_week']]
                hour = item['hour']
                count = item['count']
                print(f"  {i}. {day} {hour:02d}:00 - {count} posts")
        
        return True
    except DatabaseOperationError as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_search_posts():
    """Test search_posts function."""
    print("\n=== Testing search_posts ===")
    try:
        # Test 1: Basic pagination
        print("\n  Test 1: Basic pagination (page 1, 5 per page)")
        results = search_posts(page=1, per_page=5)
        print(f"  ✓ Retrieved {len(results['posts'])} posts")
        print(f"    Total: {results['total']}, Pages: {results['total_pages']}")
        
        # Test 2: Search with term
        print("\n  Test 2: Search with term")
        results = search_posts(search_term="instagram", page=1, per_page=5)
        print(f"  ✓ Found {results['total']} posts matching 'instagram'")
        
        # Test 3: Filter by date range
        print("\n  Test 3: Filter by date range")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        results = search_posts(filters=filters, page=1, per_page=5)
        print(f"  ✓ Found {results['total']} posts in last 7 days")
        
        # Test 4: Sort by likes
        print("\n  Test 4: Sort by likes (descending)")
        filters = {'sort_by': 'likes', 'sort_order': 'desc'}
        results = search_posts(filters=filters, page=1, per_page=3)
        if results['posts']:
            print(f"  ✓ Top posts by likes:")
            for i, post in enumerate(results['posts'], 1):
                print(f"    {i}. {post.get('author', 'N/A')}: {post.get('likes', 0)} likes")
        
        return True
    except DatabaseOperationError as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Database Query Functions")
    print("=" * 60)
    
    tests = [
        ("get_posts_with_sentiment", test_get_posts_with_sentiment),
        ("get_sentiment_distribution", test_get_sentiment_distribution),
        ("get_top_posts_by_engagement", test_get_top_posts_by_engagement),
        ("get_hashtag_frequency", test_get_hashtag_frequency),
        ("get_posting_time_heatmap", test_get_posting_time_heatmap),
        ("search_posts", test_search_posts),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Test {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
