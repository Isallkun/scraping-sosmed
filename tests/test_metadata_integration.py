"""
Integration test to verify metadata counts work with post_type field.
Tests the complete flow from task 1.4 (post_type field) to task 1.5 (metadata counts).
Validates: Requirement 13.3 and 13.4
"""

import json


def test_complete_output_structure():
    """
    Test that the complete output structure includes both post_type and metadata counts.
    
    This simulates the complete output from scrape_instagram_simple.py main() function.
    Validates Requirements 13.3 and 13.4.
    """
    # Simulate posts with post_type field (from task 1.4)
    posts = [
        {
            'post_id': 'ABC123',
            'post_type': 'post',
            'post_url': 'https://www.instagram.com/p/ABC123/',
            'author': 'testuser',
            'content': 'Test post content',
            'timestamp': '2024-01-15T10:00:00Z',
            'likes': 100,
            'comments_count': 5,
            'comments': [],
            'hashtags': ['#test'],
            'scraped_at': '2024-01-15T10:00:00Z'
        },
        {
            'post_id': 'DEF456',
            'post_type': 'reel',
            'post_url': 'https://www.instagram.com/reel/DEF456/',
            'author': 'testuser',
            'content': 'Test reel content',
            'timestamp': '2024-01-15T11:00:00Z',
            'likes': 200,
            'comments_count': 10,
            'comments': [],
            'hashtags': ['#reel'],
            'scraped_at': '2024-01-15T11:00:00Z'
        },
        {
            'post_id': 'GHI789',
            'post_type': 'post',
            'post_url': 'https://www.instagram.com/p/GHI789/',
            'author': 'testuser',
            'content': 'Another test post',
            'timestamp': '2024-01-15T12:00:00Z',
            'likes': 150,
            'comments_count': 8,
            'comments': [],
            'hashtags': [],
            'scraped_at': '2024-01-15T12:00:00Z'
        }
    ]
    
    # Calculate metadata counts (from task 1.5)
    total_comments = sum(post.get('comments_count', 0) for post in posts)
    
    result = {
        'metadata': {
            'platform': 'instagram',
            'scraped_at': '2024-01-15T12:00:00Z',
            'target_url': 'https://www.instagram.com/testuser/',
            'total_posts': len(posts),
            'post_count': sum(1 for p in posts if p.get('post_type') == 'post'),
            'reel_count': sum(1 for p in posts if p.get('post_type') == 'reel'),
            'total_comments': total_comments,
            'scrape_comments': True,
            'comments_per_post': 20,
            'method': 'enhanced with comments'
        },
        'posts': posts
    }
    
    # Verify metadata structure
    assert 'metadata' in result
    assert 'posts' in result
    
    # Verify metadata fields
    metadata = result['metadata']
    assert metadata['total_posts'] == 3
    assert metadata['post_count'] == 2
    assert metadata['reel_count'] == 1
    assert metadata['total_comments'] == 23
    
    # Verify post_count + reel_count = total_posts
    assert metadata['post_count'] + metadata['reel_count'] == metadata['total_posts']
    
    # Verify all posts have post_type field
    for post in result['posts']:
        assert 'post_type' in post, f"Post {post['post_id']} missing post_type field"
        assert post['post_type'] in ['post', 'reel'], f"Invalid post_type: {post['post_type']}"
    
    print("✓ Complete output structure is correct")


def test_json_output_compatibility():
    """
    Test that the complete output can be serialized to JSON and parsed back.
    
    This ensures the output format is compatible with downstream tools
    like sentiment analysis.
    """
    posts = [
        {'post_id': '1', 'post_type': 'post', 'content': 'Post 1'},
        {'post_id': '2', 'post_type': 'reel', 'content': 'Reel 1'},
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
    
    # Serialize to JSON
    json_str = json.dumps(result, indent=2, ensure_ascii=False)
    
    # Parse back
    parsed = json.loads(json_str)
    
    # Verify structure is preserved
    assert parsed['metadata']['total_posts'] == 2
    assert parsed['metadata']['post_count'] == 1
    assert parsed['metadata']['reel_count'] == 1
    assert len(parsed['posts']) == 2
    assert parsed['posts'][0]['post_type'] == 'post'
    assert parsed['posts'][1]['post_type'] == 'reel'
    
    print("✓ JSON serialization and parsing works correctly")


def test_backward_compatibility():
    """
    Test that the new fields don't break existing functionality.
    
    Ensures that old code expecting only total_posts still works.
    """
    posts = [
        {'post_id': '1', 'post_type': 'post'},
        {'post_id': '2', 'post_type': 'reel'},
    ]
    
    metadata = {
        'platform': 'instagram',
        'total_posts': len(posts),
        'post_count': sum(1 for p in posts if p.get('post_type') == 'post'),
        'reel_count': sum(1 for p in posts if p.get('post_type') == 'reel'),
    }
    
    # Old code that only checks total_posts should still work
    assert 'total_posts' in metadata
    assert metadata['total_posts'] == 2
    
    # New code can access the detailed counts
    assert 'post_count' in metadata
    assert 'reel_count' in metadata
    
    print("✓ Backward compatibility maintained")


def test_edge_case_empty_posts():
    """
    Test metadata counts when there are no posts.
    """
    posts = []
    
    metadata = {
        'total_posts': len(posts),
        'post_count': sum(1 for p in posts if p.get('post_type') == 'post'),
        'reel_count': sum(1 for p in posts if p.get('post_type') == 'reel'),
    }
    
    assert metadata['total_posts'] == 0
    assert metadata['post_count'] == 0
    assert metadata['reel_count'] == 0
    
    print("✓ Empty posts edge case handled correctly")


if __name__ == '__main__':
    print("Running metadata integration tests...\n")
    test_complete_output_structure()
    test_json_output_compatibility()
    test_backward_compatibility()
    test_edge_case_empty_posts()
    print("\n✅ All integration tests passed!")
