"""
Unit tests for app/services/utils.py utility functions.

Tests cover sentiment classification, engagement rate calculation,
and hashtag extraction functionality.
"""

import pytest
from app.services.utils import (
    classify_sentiment,
    calculate_engagement_rate,
    extract_hashtags
)


class TestClassifySentiment:
    """Test cases for classify_sentiment function."""
    
    def test_positive_sentiment_boundary(self):
        """Test that scores just above 0.05 are classified as positive."""
        assert classify_sentiment(0.051) == 'positive'
        assert classify_sentiment(0.06) == 'positive'
    
    def test_positive_sentiment_high_score(self):
        """Test that high positive scores are classified as positive."""
        assert classify_sentiment(0.5) == 'positive'
        assert classify_sentiment(1.0) == 'positive'
    
    def test_negative_sentiment_boundary(self):
        """Test that scores just below -0.05 are classified as negative."""
        assert classify_sentiment(-0.051) == 'negative'
        assert classify_sentiment(-0.06) == 'negative'
    
    def test_negative_sentiment_low_score(self):
        """Test that low negative scores are classified as negative."""
        assert classify_sentiment(-0.5) == 'negative'
        assert classify_sentiment(-1.0) == 'negative'
    
    def test_neutral_sentiment_zero(self):
        """Test that zero is classified as neutral."""
        assert classify_sentiment(0.0) == 'neutral'
    
    def test_neutral_sentiment_positive_boundary(self):
        """Test that scores at or just below 0.05 are classified as neutral."""
        assert classify_sentiment(0.05) == 'neutral'
        assert classify_sentiment(0.04) == 'neutral'
    
    def test_neutral_sentiment_negative_boundary(self):
        """Test that scores at or just above -0.05 are classified as neutral."""
        assert classify_sentiment(-0.05) == 'neutral'
        assert classify_sentiment(-0.04) == 'neutral'
    
    def test_neutral_sentiment_small_values(self):
        """Test that small values near zero are classified as neutral."""
        assert classify_sentiment(0.01) == 'neutral'
        assert classify_sentiment(-0.01) == 'neutral'


class TestCalculateEngagementRate:
    """Test cases for calculate_engagement_rate function."""
    
    def test_basic_engagement_calculation(self):
        """Test basic engagement rate calculation."""
        # (100 + 50) / 1000 * 100 = 15.0
        assert calculate_engagement_rate(100, 50, 1000) == 15.0
    
    def test_zero_followers_returns_zero(self):
        """Test that zero followers returns 0.0 to avoid division by zero."""
        assert calculate_engagement_rate(100, 50, 0) == 0.0
        assert calculate_engagement_rate(0, 0, 0) == 0.0
    
    def test_zero_engagement(self):
        """Test that zero likes and comments returns 0.0."""
        assert calculate_engagement_rate(0, 0, 1000) == 0.0
    
    def test_high_engagement_rate(self):
        """Test calculation with high engagement rate."""
        # (500 + 300) / 1000 * 100 = 80.0
        assert calculate_engagement_rate(500, 300, 1000) == 80.0
    
    def test_low_engagement_rate(self):
        """Test calculation with low engagement rate."""
        # (1 + 1) / 10000 * 100 = 0.02
        assert calculate_engagement_rate(1, 1, 10000) == 0.02
    
    def test_engagement_rate_over_100(self):
        """Test that engagement rate can exceed 100% (viral content)."""
        # (1000 + 500) / 1000 * 100 = 150.0
        assert calculate_engagement_rate(1000, 500, 1000) == 150.0
    
    def test_only_likes_no_comments(self):
        """Test engagement rate with only likes."""
        # (100 + 0) / 1000 * 100 = 10.0
        assert calculate_engagement_rate(100, 0, 1000) == 10.0
    
    def test_only_comments_no_likes(self):
        """Test engagement rate with only comments."""
        # (0 + 50) / 1000 * 100 = 5.0
        assert calculate_engagement_rate(0, 50, 1000) == 5.0
    
    def test_small_follower_count(self):
        """Test engagement rate with small follower count."""
        # (10 + 5) / 50 * 100 = 30.0
        assert calculate_engagement_rate(10, 5, 50) == 30.0


class TestExtractHashtags:
    """Test cases for extract_hashtags function."""
    
    def test_single_hashtag(self):
        """Test extraction of a single hashtag."""
        assert extract_hashtags("#python") == ['python']
    
    def test_multiple_hashtags(self):
        """Test extraction of multiple hashtags."""
        result = extract_hashtags("Love this! #python #coding #dev")
        assert result == ['python', 'coding', 'dev']
    
    def test_no_hashtags(self):
        """Test that captions without hashtags return empty list."""
        assert extract_hashtags("No hashtags here") == []
        assert extract_hashtags("") == []
    
    def test_hashtags_with_numbers(self):
        """Test extraction of hashtags containing numbers."""
        result = extract_hashtags("#python3 #web2 #ai2024")
        assert result == ['python3', 'web2', 'ai2024']
    
    def test_hashtags_with_underscores(self):
        """Test extraction of hashtags containing underscores."""
        result = extract_hashtags("#machine_learning #data_science")
        assert result == ['machine_learning', 'data_science']
    
    def test_duplicate_hashtags(self):
        """Test that duplicate hashtags are preserved in order."""
        result = extract_hashtags("#first #second #first")
        assert result == ['first', 'second', 'first']
    
    def test_hashtags_at_start_middle_end(self):
        """Test hashtags at different positions in caption."""
        result = extract_hashtags("#start middle #middle end #end")
        assert result == ['start', 'middle', 'end']
    
    def test_hashtags_without_spaces(self):
        """Test consecutive hashtags without spaces."""
        result = extract_hashtags("#tag1#tag2#tag3")
        assert result == ['tag1', 'tag2', 'tag3']
    
    def test_hashtags_with_special_characters_boundary(self):
        """Test that hashtags stop at special characters."""
        # Hashtags should only contain word characters (\w = alphanumeric + underscore)
        result = extract_hashtags("#python! #coding? #dev.")
        assert result == ['python', 'coding', 'dev']
    
    def test_hashtag_case_preserved(self):
        """Test that hashtag case is preserved."""
        result = extract_hashtags("#Python #CODING #Dev")
        assert result == ['Python', 'CODING', 'Dev']
    
    def test_multiline_caption(self):
        """Test hashtag extraction from multiline captions."""
        caption = """Great post!
        #python #coding
        #development"""
        result = extract_hashtags(caption)
        assert result == ['python', 'coding', 'development']
    
    def test_hashtag_only_caption(self):
        """Test caption that is only hashtags."""
        result = extract_hashtags("#tag1 #tag2 #tag3 #tag4")
        assert result == ['tag1', 'tag2', 'tag3', 'tag4']
