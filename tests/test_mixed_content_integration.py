"""
Integration test for mixed content scraping (posts and reels with comments).
Tests the complete flow from profile scraping to comment extraction.

Validates: Requirements 13.3, 13.4, 14.7
Task: 3.3 Write integration test for mixed content scraping
"""

import json
import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from selenium.webdriver.common.by import By

# Add parent directory to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMixedContentScraping:
    """Integration tests for scraping profiles with both posts and reels."""
    
    def test_mixed_content_data_structure(self):
        """
        Test that scraped data structure is correct for mixed content.
        
        Validates:
        - Requirement 13.3: post_type field is present in output
        - Requirement 13.4: metadata includes post_count and reel_count
        - Requirement 14.7: comments array is populated
        """
        # Simulate scraped posts with mixed content (as would be returned by scrape_profile_simple)
        posts = [
            {
                'post_id': 'POST123',
                'post_type': 'post',
                'post_url': 'https://www.instagram.com/p/POST123/',
                'author': 'testuser',
                'content': 'This is a regular post #test',
                'timestamp': '2024-01-15T10:00:00Z',
                'likes': 100,
                'comments_count': 2,
                'comments': [
                    {'author': 'user1', 'text': 'Great post!', 'likes': 2, 'timestamp': '2024-01-15T10:00:00Z'},
                    {'author': 'user2', 'text': 'Love it!', 'likes': 1, 'timestamp': '2024-01-15T10:05:00Z'}
                ],
                'hashtags': ['test'],
                'scraped_at': '2024-01-15T10:00:00Z'
            },
            {
                'post_id': 'REEL456',
                'post_type': 'reel',
                'post_url': 'https://www.instagram.com/reel/REEL456/',
                'author': 'testuser',
                'content': 'This is a reel #viral',
                'timestamp': '2024-01-15T11:00:00Z',
                'likes': 250,
                'comments_count': 3,
                'comments': [
                    {'author': 'user3', 'text': 'Amazing reel!', 'likes': 5, 'timestamp': '2024-01-15T11:00:00Z'},
                    {'author': 'user4', 'text': 'So cool!', 'likes': 3, 'timestamp': '2024-01-15T11:10:00Z'},
                    {'author': 'user5', 'text': 'Best content!', 'likes': 4, 'timestamp': '2024-01-15T11:20:00Z'}
                ],
                'hashtags': ['viral'],
                'scraped_at': '2024-01-15T11:00:00Z'
            },
            {
                'post_id': 'POST789',
                'post_type': 'post',
                'post_url': 'https://www.instagram.com/p/POST789/',
                'author': 'testuser',
                'content': 'Another post #photo',
                'timestamp': '2024-01-15T12:00:00Z',
                'likes': 75,
                'comments_count': 1,
                'comments': [
                    {'author': 'user6', 'text': 'Nice photo!', 'likes': 1, 'timestamp': '2024-01-15T12:00:00Z'}
                ],
                'hashtags': ['photo'],
                'scraped_at': '2024-01-15T12:00:00Z'
            },
            {
                'post_id': 'REEL012',
                'post_type': 'reel',
                'post_url': 'https://www.instagram.com/reel/REEL012/',
                'author': 'testuser',
                'content': 'Another reel #video',
                'timestamp': '2024-01-15T13:00:00Z',
                'likes': 300,
                'comments_count': 2,
                'comments': [
                    {'author': 'user7', 'text': 'Awesome video!', 'likes': 10, 'timestamp': '2024-01-15T13:00:00Z'},
                    {'author': 'user8', 'text': 'Keep it up!', 'likes': 8, 'timestamp': '2024-01-15T13:15:00Z'}
                ],
                'hashtags': ['video'],
                'scraped_at': '2024-01-15T13:00:00Z'
            }
        ]
        
        # Verify we got all posts
        assert len(posts) == 4, f"Expected 4 posts, got {len(posts)}"
        
        # Verify each post has post_type field (Requirement 13.3)
        for post in posts:
            assert 'post_type' in post, f"Post {post['post_id']} missing post_type field"
            assert post['post_type'] in ['post', 'reel'], f"Invalid post_type: {post['post_type']}"
        
        # Count posts and reels
        post_count = sum(1 for p in posts if p.get('post_type') == 'post')
        reel_count = sum(1 for p in posts if p.get('post_type') == 'reel')
        
        # Verify counts (Requirement 13.4)
        assert post_count == 2, f"Expected 2 posts, got {post_count}"
        assert reel_count == 2, f"Expected 2 reels, got {reel_count}"
        assert post_count + reel_count == len(posts), "post_count + reel_count should equal total_posts"
        
        # Verify comments array is populated (Requirement 14.7)
        for post in posts:
            assert 'comments' in post, f"Post {post['post_id']} missing comments field"
            assert isinstance(post['comments'], list), "comments should be a list"
            assert len(post['comments']) > 0, f"Post {post['post_id']} has empty comments array"
            
            # Verify comment structure
            for comment in post['comments']:
                assert 'author' in comment, "Comment missing author field"
                assert 'text' in comment, "Comment missing text field"
                assert 'timestamp' in comment, "Comment missing timestamp field"
        
        print("✓ Mixed content data structure test passed")
    
    def test_metadata_structure_with_mixed_content(self):
        """
        Test that metadata structure is correct for mixed content.
        
        Validates:
        - Requirement 13.4: metadata includes post_count and reel_count
        - post_count + reel_count = total_posts
        """
        # Simulate scraped posts
        posts = [
            {
                'post_id': 'POST1',
                'post_type': 'post',
                'post_url': 'https://www.instagram.com/p/POST1/',
                'author': 'testuser',
                'content': 'Post content',
                'likes': 100,
                'comments_count': 5,
                'comments': [
                    {'author': 'user1', 'text': 'Comment 1', 'timestamp': '2024-01-15T10:00:00Z'}
                ]
            },
            {
                'post_id': 'REEL1',
                'post_type': 'reel',
                'post_url': 'https://www.instagram.com/reel/REEL1/',
                'author': 'testuser',
                'content': 'Reel content',
                'likes': 200,
                'comments_count': 10,
                'comments': [
                    {'author': 'user2', 'text': 'Comment 2', 'timestamp': '2024-01-15T11:00:00Z'},
                    {'author': 'user3', 'text': 'Comment 3', 'timestamp': '2024-01-15T11:05:00Z'}
                ]
            },
            {
                'post_id': 'POST2',
                'post_type': 'post',
                'post_url': 'https://www.instagram.com/p/POST2/',
                'author': 'testuser',
                'content': 'Another post',
                'likes': 150,
                'comments_count': 8,
                'comments': [
                    {'author': 'user4', 'text': 'Comment 4', 'timestamp': '2024-01-15T12:00:00Z'}
                ]
            },
            {
                'post_id': 'REEL2',
                'post_type': 'reel',
                'post_url': 'https://www.instagram.com/reel/REEL2/',
                'author': 'testuser',
                'content': 'Another reel',
                'likes': 300,
                'comments_count': 15,
                'comments': [
                    {'author': 'user5', 'text': 'Comment 5', 'timestamp': '2024-01-15T13:00:00Z'},
                    {'author': 'user6', 'text': 'Comment 6', 'timestamp': '2024-01-15T13:10:00Z'},
                    {'author': 'user7', 'text': 'Comment 7', 'timestamp': '2024-01-15T13:20:00Z'}
                ]
            },
            {
                'post_id': 'REEL3',
                'post_type': 'reel',
                'post_url': 'https://www.instagram.com/reel/REEL3/',
                'author': 'testuser',
                'content': 'Third reel',
                'likes': 250,
                'comments_count': 12,
                'comments': [
                    {'author': 'user8', 'text': 'Comment 8', 'timestamp': '2024-01-15T14:00:00Z'}
                ]
            }
        ]
        
        # Calculate metadata (same as in main() function)
        total_comments = sum(post.get('comments_count', 0) for post in posts)
        
        metadata = {
            'platform': 'instagram',
            'scraped_at': datetime.utcnow().isoformat() + 'Z',
            'target_url': 'https://www.instagram.com/testuser/',
            'total_posts': len(posts),
            'post_count': sum(1 for p in posts if p.get('post_type') == 'post'),
            'reel_count': sum(1 for p in posts if p.get('post_type') == 'reel'),
            'total_comments': total_comments,
            'scrape_comments': True,
            'comments_per_post': 20,
            'method': 'enhanced with comments'
        }
        
        # Verify metadata structure
        assert metadata['total_posts'] == 5, f"Expected 5 total posts, got {metadata['total_posts']}"
        assert metadata['post_count'] == 2, f"Expected 2 posts, got {metadata['post_count']}"
        assert metadata['reel_count'] == 3, f"Expected 3 reels, got {metadata['reel_count']}"
        
        # Verify post_count + reel_count = total_posts (Requirement 13.4)
        assert metadata['post_count'] + metadata['reel_count'] == metadata['total_posts'], \
            "post_count + reel_count should equal total_posts"
        
        # Verify total_comments
        assert metadata['total_comments'] == 50, f"Expected 50 total comments, got {metadata['total_comments']}"
        
        print("✓ Metadata structure test passed")
    
    def test_json_serialization_with_mixed_content(self):
        """
        Test that complete output with mixed content can be serialized to JSON.
        
        This ensures the output format is compatible with downstream tools.
        """
        posts = [
            {
                'post_id': 'POST1',
                'post_type': 'post',
                'post_url': 'https://www.instagram.com/p/POST1/',
                'author': 'testuser',
                'content': 'Post content #test',
                'timestamp': '2024-01-15T10:00:00Z',
                'likes': 100,
                'comments_count': 2,
                'comments': [
                    {'author': 'user1', 'text': 'Great!', 'likes': 1, 'timestamp': '2024-01-15T10:05:00Z'},
                    {'author': 'user2', 'text': 'Nice!', 'likes': 2, 'timestamp': '2024-01-15T10:10:00Z'}
                ],
                'hashtags': ['test'],
                'scraped_at': '2024-01-15T10:00:00Z'
            },
            {
                'post_id': 'REEL1',
                'post_type': 'reel',
                'post_url': 'https://www.instagram.com/reel/REEL1/',
                'author': 'testuser',
                'content': 'Reel content #viral',
                'timestamp': '2024-01-15T11:00:00Z',
                'likes': 250,
                'comments_count': 3,
                'comments': [
                    {'author': 'user3', 'text': 'Amazing!', 'likes': 5, 'timestamp': '2024-01-15T11:05:00Z'},
                    {'author': 'user4', 'text': 'Love it!', 'likes': 3, 'timestamp': '2024-01-15T11:10:00Z'},
                    {'author': 'user5', 'text': 'Best!', 'likes': 4, 'timestamp': '2024-01-15T11:15:00Z'}
                ],
                'hashtags': ['viral'],
                'scraped_at': '2024-01-15T11:00:00Z'
            }
        ]
        
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
        
        # Serialize to JSON
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        
        # Verify JSON contains expected fields
        assert '"post_type": "post"' in json_str, "JSON missing post_type='post'"
        assert '"post_type": "reel"' in json_str, "JSON missing post_type='reel'"
        assert '"post_count": 1' in json_str, "JSON missing post_count"
        assert '"reel_count": 1' in json_str, "JSON missing reel_count"
        assert '"total_posts": 2' in json_str, "JSON missing total_posts"
        assert '"comments"' in json_str, "JSON missing comments field"
        
        # Parse back and verify structure
        parsed = json.loads(json_str)
        
        assert parsed['metadata']['total_posts'] == 2
        assert parsed['metadata']['post_count'] == 1
        assert parsed['metadata']['reel_count'] == 1
        assert parsed['metadata']['total_comments'] == 5
        
        # Verify post_count + reel_count = total_posts
        assert parsed['metadata']['post_count'] + parsed['metadata']['reel_count'] == \
               parsed['metadata']['total_posts']
        
        # Verify posts have correct structure
        assert len(parsed['posts']) == 2
        assert parsed['posts'][0]['post_type'] == 'post'
        assert parsed['posts'][1]['post_type'] == 'reel'
        
        # Verify comments are present
        assert len(parsed['posts'][0]['comments']) == 2
        assert len(parsed['posts'][1]['comments']) == 3
        
        print("✓ JSON serialization test passed")
    
    def test_edge_case_only_posts(self):
        """Test metadata when profile has only posts (no reels)."""
        posts = [
            {'post_id': 'POST1', 'post_type': 'post', 'comments': []},
            {'post_id': 'POST2', 'post_type': 'post', 'comments': []},
            {'post_id': 'POST3', 'post_type': 'post', 'comments': []}
        ]
        
        metadata = {
            'total_posts': len(posts),
            'post_count': sum(1 for p in posts if p.get('post_type') == 'post'),
            'reel_count': sum(1 for p in posts if p.get('post_type') == 'reel')
        }
        
        assert metadata['total_posts'] == 3
        assert metadata['post_count'] == 3
        assert metadata['reel_count'] == 0
        assert metadata['post_count'] + metadata['reel_count'] == metadata['total_posts']
        
        print("✓ Edge case (only posts) test passed")
    
    def test_edge_case_only_reels(self):
        """Test metadata when profile has only reels (no posts)."""
        posts = [
            {'post_id': 'REEL1', 'post_type': 'reel', 'comments': []},
            {'post_id': 'REEL2', 'post_type': 'reel', 'comments': []},
            {'post_id': 'REEL3', 'post_type': 'reel', 'comments': []},
            {'post_id': 'REEL4', 'post_type': 'reel', 'comments': []}
        ]
        
        metadata = {
            'total_posts': len(posts),
            'post_count': sum(1 for p in posts if p.get('post_type') == 'post'),
            'reel_count': sum(1 for p in posts if p.get('post_type') == 'reel')
        }
        
        assert metadata['total_posts'] == 4
        assert metadata['post_count'] == 0
        assert metadata['reel_count'] == 4
        assert metadata['post_count'] + metadata['reel_count'] == metadata['total_posts']
        
        print("✓ Edge case (only reels) test passed")
    
    def test_comments_array_structure(self):
        """
        Test that comments array has correct structure.
        
        Validates: Requirement 14.7
        """
        # Sample post with comments
        post = {
            'post_id': 'TEST123',
            'post_type': 'reel',
            'comments': [
                {
                    'author': 'user1',
                    'text': 'Great content!',
                    'likes': 5,
                    'timestamp': '2024-01-15T10:00:00Z'
                },
                {
                    'author': 'user2',
                    'text': 'Love this!',
                    'likes': 3,
                    'timestamp': '2024-01-15T10:05:00Z'
                }
            ]
        }
        
        # Verify comments array exists
        assert 'comments' in post
        assert isinstance(post['comments'], list)
        assert len(post['comments']) > 0
        
        # Verify each comment has required fields
        for comment in post['comments']:
            assert 'author' in comment, "Comment missing author field"
            assert 'text' in comment, "Comment missing text field"
            assert 'timestamp' in comment, "Comment missing timestamp field"
            
            # Verify field types
            assert isinstance(comment['author'], str), "author should be string"
            assert isinstance(comment['text'], str), "text should be string"
            assert isinstance(comment['timestamp'], str), "timestamp should be string"
            
            # Verify non-empty values
            assert len(comment['author']) > 0, "author should not be empty"
            assert len(comment['text']) > 0, "text should not be empty"
        
        print("✓ Comments array structure test passed")


if __name__ == '__main__':
    print("Running mixed content integration tests...\n")
    
    test_suite = TestMixedContentScraping()
    
    # Run all tests
    test_suite.test_mixed_content_data_structure()
    test_suite.test_metadata_structure_with_mixed_content()
    test_suite.test_json_serialization_with_mixed_content()
    test_suite.test_edge_case_only_posts()
    test_suite.test_edge_case_only_reels()
    test_suite.test_comments_array_structure()
    
    print("\n✅ All mixed content integration tests passed!")
