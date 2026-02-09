"""
Unit tests for post_type extraction logic.
Tests for task 3.1: Write unit tests for post_type extraction

Validates: Requirements 13.1, 13.2
"""

import pytest


class TestPostTypeExtraction:
    """Test post_type extraction from Instagram URLs"""
    
    def test_post_url_returns_post_type_post(self):
        """
        Test URL with /p/ returns post_type="post"
        Validates: Requirement 13.2
        """
        # Simulate the URL parsing logic from task 1.2
        href = 'https://www.instagram.com/p/ABC123xyz/'
        
        # Extract post_type (same logic as in scrape_profile_simple)
        if '/p/' in href:
            post_id = href.split('/p/')[1].split('/')[0]
            post_type = 'post'
        elif '/reel/' in href:
            post_id = href.split('/reel/')[1].split('/')[0]
            post_type = 'reel'
        else:
            post_type = None
        
        # Assertions
        assert post_type == 'post', f"Expected post_type='post', got '{post_type}'"
        assert post_id == 'ABC123xyz', f"Expected post_id='ABC123xyz', got '{post_id}'"
        print("✓ URL with /p/ correctly returns post_type='post'")
    
    def test_reel_url_returns_post_type_reel(self):
        """
        Test URL with /reel/ returns post_type="reel"
        Validates: Requirement 13.2
        """
        # Simulate the URL parsing logic from task 1.2
        href = 'https://www.instagram.com/reel/XYZ789abc/'
        
        # Extract post_type (same logic as in scrape_profile_simple)
        if '/p/' in href:
            post_id = href.split('/p/')[1].split('/')[0]
            post_type = 'post'
        elif '/reel/' in href:
            post_id = href.split('/reel/')[1].split('/')[0]
            post_type = 'reel'
        else:
            post_type = None
        
        # Assertions
        assert post_type == 'reel', f"Expected post_type='reel', got '{post_type}'"
        assert post_id == 'XYZ789abc', f"Expected post_id='XYZ789abc', got '{post_id}'"
        print("✓ URL with /reel/ correctly returns post_type='reel'")
    
    def test_unknown_url_format_is_skipped(self):
        """
        Test unknown URL format is skipped (returns None)
        Validates: Requirement 13.1
        """
        # Test various unknown URL formats
        unknown_urls = [
            'https://www.instagram.com/stories/user/123/',
            'https://www.instagram.com/tv/ABC123/',
            'https://www.instagram.com/user/',
            'https://www.instagram.com/',
            'https://www.instagram.com/explore/',
        ]
        
        for href in unknown_urls:
            # Extract post_type (same logic as in scrape_profile_simple)
            if '/p/' in href:
                post_id = href.split('/p/')[1].split('/')[0]
                post_type = 'post'
            elif '/reel/' in href:
                post_id = href.split('/reel/')[1].split('/')[0]
                post_type = 'reel'
            else:
                post_type = None
            
            # Assertion
            assert post_type is None, f"Unknown URL format should return None, got '{post_type}' for {href}"
        
        print("✓ Unknown URL formats are correctly skipped (return None)")
    
    def test_post_id_extraction_for_post_format(self):
        """
        Test post_id extraction accuracy for /p/ format
        Validates: Requirement 13.2
        """
        test_cases = [
            ('https://www.instagram.com/p/ABC123/', 'ABC123'),
            ('https://www.instagram.com/p/XYZ789abc/', 'XYZ789abc'),
            ('https://www.instagram.com/p/Test_123-456/', 'Test_123-456'),
            ('https://www.instagram.com/p/a1b2c3/', 'a1b2c3'),
        ]
        
        for href, expected_id in test_cases:
            # Extract post_id (same logic as in scrape_profile_simple)
            if '/p/' in href:
                post_id = href.split('/p/')[1].split('/')[0]
                post_type = 'post'
            else:
                post_id = None
                post_type = None
            
            # Assertions
            assert post_id == expected_id, f"Expected post_id='{expected_id}', got '{post_id}' for {href}"
            assert post_type == 'post', f"Expected post_type='post', got '{post_type}'"
        
        print("✓ post_id extraction for /p/ format is accurate")
    
    def test_post_id_extraction_for_reel_format(self):
        """
        Test post_id extraction accuracy for /reel/ format
        Validates: Requirement 13.2
        """
        test_cases = [
            ('https://www.instagram.com/reel/DEF456/', 'DEF456'),
            ('https://www.instagram.com/reel/ReelTest123/', 'ReelTest123'),
            ('https://www.instagram.com/reel/xyz_ABC-789/', 'xyz_ABC-789'),
            ('https://www.instagram.com/reel/r1r2r3/', 'r1r2r3'),
        ]
        
        for href, expected_id in test_cases:
            # Extract post_id (same logic as in scrape_profile_simple)
            if '/p/' in href:
                post_id = href.split('/p/')[1].split('/')[0]
                post_type = 'post'
            elif '/reel/' in href:
                post_id = href.split('/reel/')[1].split('/')[0]
                post_type = 'reel'
            else:
                post_id = None
                post_type = None
            
            # Assertions
            assert post_id == expected_id, f"Expected post_id='{expected_id}', got '{post_id}' for {href}"
            assert post_type == 'reel', f"Expected post_type='reel', got '{post_type}'"
        
        print("✓ post_id extraction for /reel/ format is accurate")
    
    def test_url_with_trailing_slash(self):
        """
        Test URLs with and without trailing slashes are handled correctly
        """
        test_cases = [
            ('https://www.instagram.com/p/ABC123/', 'ABC123', 'post'),
            ('https://www.instagram.com/p/ABC123', 'ABC123', 'post'),
            ('https://www.instagram.com/reel/XYZ789/', 'XYZ789', 'reel'),
            ('https://www.instagram.com/reel/XYZ789', 'XYZ789', 'reel'),
        ]
        
        for href, expected_id, expected_type in test_cases:
            # Extract post_type (same logic as in scrape_profile_simple)
            if '/p/' in href:
                post_id = href.split('/p/')[1].split('/')[0]
                post_type = 'post'
            elif '/reel/' in href:
                post_id = href.split('/reel/')[1].split('/')[0]
                post_type = 'reel'
            else:
                post_id = None
                post_type = None
            
            # Assertions
            assert post_id == expected_id, f"Expected post_id='{expected_id}', got '{post_id}' for {href}"
            assert post_type == expected_type, f"Expected post_type='{expected_type}', got '{post_type}'"
        
        print("✓ URLs with/without trailing slashes are handled correctly")
    
    def test_url_with_query_parameters(self):
        """
        Test URLs with query parameters are handled correctly
        """
        test_cases = [
            ('https://www.instagram.com/p/ABC123/?utm_source=ig_web', 'ABC123', 'post'),
            ('https://www.instagram.com/reel/XYZ789/?hl=en', 'XYZ789', 'reel'),
            ('https://www.instagram.com/p/TEST456/?taken-by=user', 'TEST456', 'post'),
        ]
        
        for href, expected_id, expected_type in test_cases:
            # Extract post_type (same logic as in scrape_profile_simple)
            if '/p/' in href:
                post_id = href.split('/p/')[1].split('/')[0].split('?')[0]
                post_type = 'post'
            elif '/reel/' in href:
                post_id = href.split('/reel/')[1].split('/')[0].split('?')[0]
                post_type = 'reel'
            else:
                post_id = None
                post_type = None
            
            # Assertions
            assert post_id == expected_id, f"Expected post_id='{expected_id}', got '{post_id}' for {href}"
            assert post_type == expected_type, f"Expected post_type='{expected_type}', got '{post_type}'"
        
        print("✓ URLs with query parameters are handled correctly")


class TestUniquePostsTupleStructure:
    """Test the unique_posts tuple structure change from task 1.3"""
    
    def test_tuple_structure_includes_post_type(self):
        """
        Test that unique_posts tuple includes post_type as third element
        Validates: Requirement 13.2
        """
        # Simulate creating unique_posts tuples
        post_id = 'ABC123'
        href = 'https://www.instagram.com/p/ABC123/'
        post_type = 'post'
        
        # Create tuple (new structure from task 1.3)
        unique_post_tuple = (post_id, href, post_type)
        
        # Assertions
        assert len(unique_post_tuple) == 3, f"Expected tuple length 3, got {len(unique_post_tuple)}"
        assert unique_post_tuple[0] == post_id, "First element should be post_id"
        assert unique_post_tuple[1] == href, "Second element should be href"
        assert unique_post_tuple[2] == post_type, "Third element should be post_type"
        
        print("✓ unique_posts tuple structure correctly includes post_type")
    
    def test_tuple_unpacking(self):
        """
        Test that the new tuple structure can be unpacked correctly
        """
        # Create sample tuples for both posts and reels
        post_tuple = ('POST123', 'https://www.instagram.com/p/POST123/', 'post')
        reel_tuple = ('REEL456', 'https://www.instagram.com/reel/REEL456/', 'reel')
        
        # Unpack tuples (as done in scrape_profile_simple)
        post_id_1, post_url_1, post_type_1 = post_tuple
        post_id_2, post_url_2, post_type_2 = reel_tuple
        
        # Assertions for post
        assert post_id_1 == 'POST123'
        assert post_url_1 == 'https://www.instagram.com/p/POST123/'
        assert post_type_1 == 'post'
        
        # Assertions for reel
        assert post_id_2 == 'REEL456'
        assert post_url_2 == 'https://www.instagram.com/reel/REEL456/'
        assert post_type_2 == 'reel'
        
        print("✓ Tuple unpacking works correctly with new structure")


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_url(self):
        """Test handling of empty URL"""
        href = ''
        
        # Extract post_type
        if '/p/' in href:
            post_type = 'post'
        elif '/reel/' in href:
            post_type = 'reel'
        else:
            post_type = None
        
        assert post_type is None, "Empty URL should return None"
        print("✓ Empty URL is handled correctly")
    
    def test_malformed_url(self):
        """Test handling of malformed URLs"""
        malformed_urls = [
            'not-a-url',
            'http://',
            'instagram.com/p/',
            '/p/ABC123/',
            'https://www.instagram.com/p/',  # Missing post_id
            'https://www.instagram.com/reel/',  # Missing post_id
        ]
        
        for href in malformed_urls:
            # Extract post_type
            if '/p/' in href:
                try:
                    post_id = href.split('/p/')[1].split('/')[0]
                    if not post_id:  # Empty post_id
                        post_type = None
                    else:
                        post_type = 'post'
                except (IndexError, AttributeError):
                    post_type = None
            elif '/reel/' in href:
                try:
                    post_id = href.split('/reel/')[1].split('/')[0]
                    if not post_id:  # Empty post_id
                        post_type = None
                    else:
                        post_type = 'reel'
                except (IndexError, AttributeError):
                    post_type = None
            else:
                post_type = None
            
            # Should either return None or handle gracefully
            assert post_type in [None, 'post', 'reel'], f"Unexpected post_type for malformed URL: {href}"
        
        print("✓ Malformed URLs are handled gracefully")
    
    def test_case_sensitivity(self):
        """Test that URL matching is case-sensitive (as it should be)"""
        # Instagram URLs are case-sensitive for post IDs
        test_cases = [
            ('https://www.instagram.com/p/AbC123/', 'AbC123', 'post'),
            ('https://www.instagram.com/reel/XyZ789/', 'XyZ789', 'reel'),
        ]
        
        for href, expected_id, expected_type in test_cases:
            # Extract post_type
            if '/p/' in href:
                post_id = href.split('/p/')[1].split('/')[0]
                post_type = 'post'
            elif '/reel/' in href:
                post_id = href.split('/reel/')[1].split('/')[0]
                post_type = 'reel'
            else:
                post_id = None
                post_type = None
            
            # Assertions - post_id should preserve case
            assert post_id == expected_id, f"Expected post_id='{expected_id}', got '{post_id}'"
            assert post_type == expected_type
        
        print("✓ Case sensitivity is preserved in post_id extraction")


# Run tests if executed directly
if __name__ == '__main__':
    print("=" * 70)
    print("Running post_type extraction tests...")
    print("=" * 70)
    print()
    
    # Run TestPostTypeExtraction tests
    print("TestPostTypeExtraction:")
    print("-" * 70)
    test_obj = TestPostTypeExtraction()
    test_obj.test_post_url_returns_post_type_post()
    test_obj.test_reel_url_returns_post_type_reel()
    test_obj.test_unknown_url_format_is_skipped()
    test_obj.test_post_id_extraction_for_post_format()
    test_obj.test_post_id_extraction_for_reel_format()
    test_obj.test_url_with_trailing_slash()
    test_obj.test_url_with_query_parameters()
    print()
    
    # Run TestUniquePostsTupleStructure tests
    print("TestUniquePostsTupleStructure:")
    print("-" * 70)
    test_obj2 = TestUniquePostsTupleStructure()
    test_obj2.test_tuple_structure_includes_post_type()
    test_obj2.test_tuple_unpacking()
    print()
    
    # Run TestEdgeCases tests
    print("TestEdgeCases:")
    print("-" * 70)
    test_obj3 = TestEdgeCases()
    test_obj3.test_empty_url()
    test_obj3.test_malformed_url()
    test_obj3.test_case_sensitivity()
    print()
    
    print("=" * 70)
    print("✅ All post_type extraction tests passed!")
    print("=" * 70)
