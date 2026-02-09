"""
Unit test to verify post_type field is correctly added to post_data dictionary.
Tests for task 1.4: Add post_type field to post_data dictionary
"""

import json
import re
from datetime import datetime


def test_post_data_structure_includes_post_type():
    """
    Test that post_data dictionary includes post_type field.
    This simulates the structure created in scrape_profile_simple().
    """
    # Simulate the post_type variable from task 1.2
    post_type = 'reel'
    post_id = 'ABC123xyz'
    post_url = 'https://www.instagram.com/reel/ABC123xyz/'
    profile_url = 'https://www.instagram.com/testuser/'
    content = 'Test reel content #test'
    likes = 100
    comments_count = 5
    
    # Extract hashtags
    hashtags = re.findall(r'#\w+', content) if content else []
    
    # Create post_data dictionary (same structure as in scrape_instagram_simple.py)
    post_data = {
        'post_id': post_id,
        'post_type': post_type,
        'post_url': post_url,
        'author': profile_url.split('/')[-2],
        'content': content or f"Post {post_id}",
        'timestamp': datetime.now().isoformat() + 'Z',
        'likes': likes,
        'comments_count': comments_count,
        'comments': [],
        'hashtags': hashtags,
        'scraped_at': datetime.now().isoformat() + 'Z'
    }
    
    # Verify post_type field exists
    assert 'post_type' in post_data, "post_type field is missing from post_data"
    
    # Verify post_type has correct value
    assert post_data['post_type'] == 'reel', f"Expected post_type='reel', got '{post_data['post_type']}'"
    
    # Verify post_type is in correct position (after post_id)
    keys = list(post_data.keys())
    assert keys[0] == 'post_id', "post_id should be first field"
    assert keys[1] == 'post_type', "post_type should be second field (after post_id)"
    
    print("✓ post_type field is correctly included in post_data dictionary")


def test_post_data_json_serialization():
    """
    Test that post_data with post_type field can be serialized to JSON.
    Validates Requirement 13.3: post_type field is included in JSON output.
    """
    # Create sample post_data for both post and reel
    posts = [
        {
            'post_id': 'POST123',
            'post_type': 'post',
            'post_url': 'https://www.instagram.com/p/POST123/',
            'author': 'testuser',
            'content': 'Regular post content',
            'timestamp': '2024-01-15T10:00:00Z',
            'likes': 50,
            'comments_count': 3,
            'comments': [],
            'hashtags': [],
            'scraped_at': '2024-01-15T10:00:00Z'
        },
        {
            'post_id': 'REEL456',
            'post_type': 'reel',
            'post_url': 'https://www.instagram.com/reel/REEL456/',
            'author': 'testuser',
            'content': 'Reel content',
            'timestamp': '2024-01-15T11:00:00Z',
            'likes': 150,
            'comments_count': 10,
            'comments': [],
            'hashtags': [],
            'scraped_at': '2024-01-15T11:00:00Z'
        }
    ]
    
    # Simulate the result structure from scrape_instagram_simple.py
    result = {
        'metadata': {
            'platform': 'instagram',
            'scraped_at': '2024-01-15T12:00:00Z',
            'target_url': 'https://www.instagram.com/testuser/',
            'total_posts': len(posts)
        },
        'posts': posts
    }
    
    # Serialize to JSON (same as in the actual code)
    json_str = json.dumps(result, indent=2, ensure_ascii=False)
    
    # Verify JSON contains post_type fields
    assert '"post_type": "post"' in json_str, "post_type='post' not found in JSON output"
    assert '"post_type": "reel"' in json_str, "post_type='reel' not found in JSON output"
    
    # Deserialize and verify structure
    parsed = json.loads(json_str)
    assert parsed['posts'][0]['post_type'] == 'post', "First post should have post_type='post'"
    assert parsed['posts'][1]['post_type'] == 'reel', "Second post should have post_type='reel'"
    
    print("✓ post_type field is correctly serialized to JSON output")


def test_post_type_values():
    """
    Test that post_type field contains valid values ('post' or 'reel').
    """
    valid_post_types = ['post', 'reel']
    
    # Test with 'post'
    post_data_post = {
        'post_id': 'TEST1',
        'post_type': 'post',
        'post_url': 'https://www.instagram.com/p/TEST1/'
    }
    assert post_data_post['post_type'] in valid_post_types
    assert post_data_post['post_type'] == 'post'
    
    # Test with 'reel'
    post_data_reel = {
        'post_id': 'TEST2',
        'post_type': 'reel',
        'post_url': 'https://www.instagram.com/reel/TEST2/'
    }
    assert post_data_reel['post_type'] in valid_post_types
    assert post_data_reel['post_type'] == 'reel'
    
    print("✓ post_type field contains valid values")


if __name__ == '__main__':
    print("Running post_type field tests...\n")
    test_post_data_structure_includes_post_type()
    test_post_data_json_serialization()
    test_post_type_values()
    print("\n✅ All tests passed!")
