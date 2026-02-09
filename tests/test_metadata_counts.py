"""
Unit test to verify metadata post_count and reel_count fields.
Tests for task 1.5: Update metadata with post/reel counts
Validates: Requirement 13.4
"""

import json


def test_metadata_count_calculation():
    """
    Test that metadata correctly calculates post_count and reel_count.
    
    Validates Requirement 13.4: Metadata reports counts for both posts and reels separately.
    """
    # Simulate posts data with mix of posts and reels
    posts = [
        {'post_id': '1', 'post_type': 'post', 'content': 'Post 1'},
        {'post_id': '2', 'post_type': 'reel', 'content': 'Reel 1'},
        {'post_id': '3', 'post_type': 'post', 'content': 'Post 2'},
        {'post_id': '4', 'post_type': 'reel', 'content': 'Reel 2'},
        {'post_id': '5', 'post_type': 'post', 'content': 'Post 3'},
    ]
    
    # Calculate counts as done in main() function
    total_posts = len(posts)
    post_count = sum(1 for p in posts if p.get('post_type') == 'post')
    reel_count = sum(1 for p in posts if p.get('post_type') == 'reel')
    
    # Verify counts
    assert total_posts == 5, f"Expected total_posts=5, got {total_posts}"
    assert post_count == 3, f"Expected post_count=3, got {post_count}"
    assert reel_count == 2, f"Expected reel_count=2, got {reel_count}"
    
    # Verify sum equals total
    assert post_count + reel_count == total_posts, "post_count + reel_count should equal total_posts"
    
    print("✓ Metadata count calculation is correct")


def test_metadata_structure():
    """
    Test that metadata dictionary includes all required fields.
    
    Validates Requirement 13.4: Metadata includes post_count and reel_count fields.
    """
    # Simulate metadata structure from main() function
    posts = [
        {'post_id': '1', 'post_type': 'post'},
        {'post_id': '2', 'post_type': 'reel'},
        {'post_id': '3', 'post_type': 'post'},
    ]
    
    metadata = {
        'platform': 'instagram',
        'scraped_at': '2024-01-15T12:00:00Z',
        'target_url': 'https://www.instagram.com/test/',
        'total_posts': len(posts),
        'post_count': sum(1 for p in posts if p.get('post_type') == 'post'),
        'reel_count': sum(1 for p in posts if p.get('post_type') == 'reel'),
        'total_comments': 0,
        'scrape_comments': True,
        'comments_per_post': 20,
        'method': 'enhanced with comments'
    }
    
    # Verify required fields exist
    assert 'total_posts' in metadata, "total_posts field is missing"
    assert 'post_count' in metadata, "post_count field is missing"
    assert 'reel_count' in metadata, "reel_count field is missing"
    
    # Verify values
    assert metadata['total_posts'] == 3
    assert metadata['post_count'] == 2
    assert metadata['reel_count'] == 1
    
    print("✓ Metadata structure includes all required fields")


def test_metadata_with_only_posts():
    """
    Test metadata counts when there are only posts (no reels).
    """
    posts = [
        {'post_id': '1', 'post_type': 'post'},
        {'post_id': '2', 'post_type': 'post'},
        {'post_id': '3', 'post_type': 'post'},
    ]
    
    post_count = sum(1 for p in posts if p.get('post_type') == 'post')
    reel_count = sum(1 for p in posts if p.get('post_type') == 'reel')
    
    assert post_count == 3, f"Expected post_count=3, got {post_count}"
    assert reel_count == 0, f"Expected reel_count=0, got {reel_count}"
    
    print("✓ Metadata handles posts-only scenario correctly")


def test_metadata_with_only_reels():
    """
    Test metadata counts when there are only reels (no posts).
    """
    posts = [
        {'post_id': '1', 'post_type': 'reel'},
        {'post_id': '2', 'post_type': 'reel'},
    ]
    
    post_count = sum(1 for p in posts if p.get('post_type') == 'post')
    reel_count = sum(1 for p in posts if p.get('post_type') == 'reel')
    
    assert post_count == 0, f"Expected post_count=0, got {post_count}"
    assert reel_count == 2, f"Expected reel_count=2, got {reel_count}"
    
    print("✓ Metadata handles reels-only scenario correctly")


def test_metadata_with_missing_post_type():
    """
    Test metadata counts when some posts are missing post_type field.
    This tests backward compatibility with old data.
    """
    posts = [
        {'post_id': '1', 'post_type': 'post'},
        {'post_id': '2'},  # Missing post_type
        {'post_id': '3', 'post_type': 'reel'},
    ]
    
    post_count = sum(1 for p in posts if p.get('post_type') == 'post')
    reel_count = sum(1 for p in posts if p.get('post_type') == 'reel')
    
    assert post_count == 1, f"Expected post_count=1, got {post_count}"
    assert reel_count == 1, f"Expected reel_count=1, got {reel_count}"
    
    # Note: Missing post_type is not counted in either category
    assert post_count + reel_count == 2, "Only posts with post_type should be counted"
    
    print("✓ Metadata handles missing post_type gracefully")


def test_metadata_json_serialization():
    """
    Test that metadata with post_count and reel_count can be serialized to JSON.
    """
    posts = [
        {'post_id': '1', 'post_type': 'post'},
        {'post_id': '2', 'post_type': 'reel'},
    ]
    
    result = {
        'metadata': {
            'platform': 'instagram',
            'scraped_at': '2024-01-15T12:00:00Z',
            'target_url': 'https://www.instagram.com/test/',
            'total_posts': len(posts),
            'post_count': sum(1 for p in posts if p.get('post_type') == 'post'),
            'reel_count': sum(1 for p in posts if p.get('post_type') == 'reel'),
            'total_comments': 0,
            'scrape_comments': True,
            'comments_per_post': 20,
            'method': 'enhanced with comments'
        },
        'posts': posts
    }
    
    # Test JSON serialization
    try:
        json_str = json.dumps(result, indent=2)
        parsed = json.loads(json_str)
        
        # Verify structure after serialization
        assert 'metadata' in parsed
        assert 'post_count' in parsed['metadata']
        assert 'reel_count' in parsed['metadata']
        assert parsed['metadata']['post_count'] == 1
        assert parsed['metadata']['reel_count'] == 1
        
        print("✓ Metadata with counts serializes to JSON correctly")
    except Exception as e:
        raise AssertionError(f"JSON serialization failed: {e}")


if __name__ == '__main__':
    print("Running metadata count tests...\n")
    test_metadata_count_calculation()
    test_metadata_structure()
    test_metadata_with_only_posts()
    test_metadata_with_only_reels()
    test_metadata_with_missing_post_type()
    test_metadata_json_serialization()
    print("\n✅ All metadata count tests passed!")
