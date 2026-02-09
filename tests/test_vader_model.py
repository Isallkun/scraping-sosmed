"""
Unit tests for VADER sentiment model.

Tests the VADERModel class to ensure correct sentiment analysis,
classification thresholds, and output format.
"""

import pytest
from sentiment.models.vader_model import VADERModel


class TestVADERModel:
    """Test suite for VADERModel class"""
    
    @pytest.fixture
    def vader_model(self):
        """Create a VADERModel instance for testing"""
        return VADERModel()
    
    def test_initialization(self, vader_model):
        """Test that VADERModel initializes correctly"""
        assert vader_model is not None
        assert vader_model.analyzer is not None
    
    def test_positive_sentiment(self, vader_model):
        """Test analysis of clearly positive text"""
        text = "I love this! It's absolutely amazing and wonderful!"
        result = vader_model.analyze(text)
        
        assert result['label'] == 'positive'
        assert result['compound'] >= 0.05
        assert result['score'] == result['compound']
        assert result['model'] == 'vader'
        assert 0.0 <= result['confidence'] <= 1.0
    
    def test_negative_sentiment(self, vader_model):
        """Test analysis of clearly negative text"""
        text = "This is terrible! I hate it so much. Worst experience ever."
        result = vader_model.analyze(text)
        
        assert result['label'] == 'negative'
        assert result['compound'] <= -0.05
        assert result['score'] == result['compound']
        assert result['model'] == 'vader'
        assert 0.0 <= result['confidence'] <= 1.0
    
    def test_neutral_sentiment(self, vader_model):
        """Test analysis of neutral text"""
        text = "The product is available in the store."
        result = vader_model.analyze(text)
        
        assert result['label'] == 'neutral'
        assert -0.05 < result['compound'] < 0.05
        assert result['score'] == result['compound']
        assert result['model'] == 'vader'
    
    def test_empty_text(self, vader_model):
        """Test analysis of empty text"""
        result = vader_model.analyze("")
        
        assert result['label'] == 'neutral'
        assert result['compound'] == 0.0
        assert result['score'] == 0.0
        assert result['confidence'] == 0.0
        assert result['neutral'] == 1.0
        assert result['model'] == 'vader'
    
    def test_whitespace_only_text(self, vader_model):
        """Test analysis of whitespace-only text"""
        result = vader_model.analyze("   \n\t  ")
        
        assert result['label'] == 'neutral'
        assert result['compound'] == 0.0
        assert result['score'] == 0.0
        assert result['confidence'] == 0.0
    
    def test_output_structure(self, vader_model):
        """Test that output contains all required fields"""
        text = "This is a test."
        result = vader_model.analyze(text)
        
        # Check all required fields are present
        required_fields = [
            'score', 'label', 'confidence', 'compound',
            'positive', 'neutral', 'negative', 'model'
        ]
        for field in required_fields:
            assert field in result
    
    def test_score_ranges(self, vader_model):
        """Test that all scores are within valid ranges"""
        text = "This is great but also has some issues."
        result = vader_model.analyze(text)
        
        # Compound score should be between -1.0 and 1.0
        assert -1.0 <= result['compound'] <= 1.0
        assert -1.0 <= result['score'] <= 1.0
        
        # Individual scores should be between 0.0 and 1.0
        assert 0.0 <= result['positive'] <= 1.0
        assert 0.0 <= result['neutral'] <= 1.0
        assert 0.0 <= result['negative'] <= 1.0
        
        # Confidence should be between 0.0 and 1.0
        assert 0.0 <= result['confidence'] <= 1.0
    
    def test_classification_threshold_positive_boundary(self, vader_model):
        """Test classification at positive threshold boundary"""
        # Test text that should be just above positive threshold
        text = "good"
        result = vader_model.analyze(text)
        
        if result['compound'] >= 0.05:
            assert result['label'] == 'positive'
        elif result['compound'] <= -0.05:
            assert result['label'] == 'negative'
        else:
            assert result['label'] == 'neutral'
    
    def test_classification_threshold_negative_boundary(self, vader_model):
        """Test classification at negative threshold boundary"""
        # Test text that should be just below negative threshold
        text = "bad"
        result = vader_model.analyze(text)
        
        if result['compound'] >= 0.05:
            assert result['label'] == 'positive'
        elif result['compound'] <= -0.05:
            assert result['label'] == 'negative'
        else:
            assert result['label'] == 'neutral'
    
    def test_confidence_equals_abs_compound(self, vader_model):
        """Test that confidence equals absolute value of compound score"""
        texts = [
            "I love this!",
            "I hate this!",
            "This is okay."
        ]
        
        for text in texts:
            result = vader_model.analyze(text)
            assert result['confidence'] == abs(result['compound'])
    
    def test_emoji_handling(self, vader_model):
        """Test that VADER handles emojis (social media optimization)"""
        text = "I love this! 😊 👍"
        result = vader_model.analyze(text)
        
        # Should detect positive sentiment from emojis
        assert result['compound'] > 0
        assert result['label'] in ['positive', 'neutral']
    
    def test_mixed_sentiment(self, vader_model):
        """Test analysis of text with mixed sentiment"""
        text = "The product is good but the service is terrible."
        result = vader_model.analyze(text)
        
        # Should return a valid result with proper structure
        assert result['label'] in ['positive', 'negative', 'neutral']
        assert -1.0 <= result['compound'] <= 1.0
    
    def test_multiple_analyses(self, vader_model):
        """Test that model can be used for multiple analyses"""
        texts = [
            "Great!",
            "Terrible!",
            "Okay.",
            "Amazing!",
            "Awful!"
        ]
        
        for text in texts:
            result = vader_model.analyze(text)
            assert result is not None
            assert 'label' in result
            assert 'compound' in result
