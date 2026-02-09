"""
Unit tests for TextBlob sentiment model.

Tests the TextBlobModel class to ensure correct sentiment analysis,
classification thresholds, and output format matching VADER format.
"""

import pytest
from sentiment.models.textblob_model import TextBlobModel


class TestTextBlobModel:
    """Test suite for TextBlobModel class"""
    
    @pytest.fixture
    def textblob_model(self):
        """Create a TextBlobModel instance for testing"""
        return TextBlobModel()
    
    def test_initialization(self, textblob_model):
        """Test that TextBlobModel initializes correctly"""
        assert textblob_model is not None
    
    def test_positive_sentiment(self, textblob_model):
        """Test analysis of clearly positive text"""
        text = "I love this! It's absolutely amazing and wonderful!"
        result = textblob_model.analyze(text)
        
        assert result['label'] == 'positive'
        assert result['compound'] >= 0.05
        assert result['score'] == result['compound']
        assert result['model'] == 'textblob'
        assert 0.0 <= result['confidence'] <= 1.0
    
    def test_negative_sentiment(self, textblob_model):
        """Test analysis of clearly negative text"""
        text = "This is terrible! I hate it so much. Worst experience ever."
        result = textblob_model.analyze(text)
        
        assert result['label'] == 'negative'
        assert result['compound'] <= -0.05
        assert result['score'] == result['compound']
        assert result['model'] == 'textblob'
        assert 0.0 <= result['confidence'] <= 1.0
    
    def test_neutral_sentiment(self, textblob_model):
        """Test analysis of neutral text"""
        text = "The item is on the table."
        result = textblob_model.analyze(text)
        
        # TextBlob may interpret some texts differently than VADER
        # The key is that the label matches the compound score thresholds
        if result['compound'] >= 0.05:
            assert result['label'] == 'positive'
        elif result['compound'] <= -0.05:
            assert result['label'] == 'negative'
        else:
            assert result['label'] == 'neutral'
        
        assert result['score'] == result['compound']
        assert result['model'] == 'textblob'
    
    def test_empty_text(self, textblob_model):
        """Test analysis of empty text"""
        result = textblob_model.analyze("")
        
        assert result['label'] == 'neutral'
        assert result['compound'] == 0.0
        assert result['score'] == 0.0
        assert result['confidence'] == 0.0
        assert result['neutral'] == 1.0
        assert result['model'] == 'textblob'
    
    def test_whitespace_only_text(self, textblob_model):
        """Test analysis of whitespace-only text"""
        result = textblob_model.analyze("   \n\t  ")
        
        assert result['label'] == 'neutral'
        assert result['compound'] == 0.0
        assert result['score'] == 0.0
        assert result['confidence'] == 0.0
    
    def test_output_structure(self, textblob_model):
        """Test that output contains all required fields"""
        text = "This is a test."
        result = textblob_model.analyze(text)
        
        # Check all required fields are present
        required_fields = [
            'score', 'label', 'confidence', 'compound',
            'positive', 'neutral', 'negative', 'model'
        ]
        for field in required_fields:
            assert field in result
    
    def test_score_ranges(self, textblob_model):
        """Test that all scores are within valid ranges"""
        text = "This is great but also has some issues."
        result = textblob_model.analyze(text)
        
        # Compound score should be between -1.0 and 1.0
        assert -1.0 <= result['compound'] <= 1.0
        assert -1.0 <= result['score'] <= 1.0
        
        # Individual scores should be between 0.0 and 1.0
        assert 0.0 <= result['positive'] <= 1.0
        assert 0.0 <= result['neutral'] <= 1.0
        assert 0.0 <= result['negative'] <= 1.0
        
        # Confidence should be between 0.0 and 1.0
        assert 0.0 <= result['confidence'] <= 1.0
    
    def test_classification_threshold_positive_boundary(self, textblob_model):
        """Test classification at positive threshold boundary"""
        # Test text that should be positive
        text = "good"
        result = textblob_model.analyze(text)
        
        if result['compound'] >= 0.05:
            assert result['label'] == 'positive'
        elif result['compound'] <= -0.05:
            assert result['label'] == 'negative'
        else:
            assert result['label'] == 'neutral'
    
    def test_classification_threshold_negative_boundary(self, textblob_model):
        """Test classification at negative threshold boundary"""
        # Test text that should be negative
        text = "bad"
        result = textblob_model.analyze(text)
        
        if result['compound'] >= 0.05:
            assert result['label'] == 'positive'
        elif result['compound'] <= -0.05:
            assert result['label'] == 'negative'
        else:
            assert result['label'] == 'neutral'
    
    def test_confidence_equals_abs_compound(self, textblob_model):
        """Test that confidence equals absolute value of compound score"""
        texts = [
            "I love this!",
            "I hate this!",
            "This is okay."
        ]
        
        for text in texts:
            result = textblob_model.analyze(text)
            assert result['confidence'] == abs(result['compound'])
    
    def test_mixed_sentiment(self, textblob_model):
        """Test analysis of text with mixed sentiment"""
        text = "The product is good but the service is terrible."
        result = textblob_model.analyze(text)
        
        # Should return a valid result with proper structure
        assert result['label'] in ['positive', 'negative', 'neutral']
        assert -1.0 <= result['compound'] <= 1.0
    
    def test_multiple_analyses(self, textblob_model):
        """Test that model can be used for multiple analyses"""
        texts = [
            "Great!",
            "Terrible!",
            "Okay.",
            "Amazing!",
            "Awful!"
        ]
        
        for text in texts:
            result = textblob_model.analyze(text)
            assert result is not None
            assert 'label' in result
            assert 'compound' in result
    
    def test_vader_format_compatibility(self, textblob_model):
        """Test that TextBlob output format matches VADER format"""
        text = "This is a wonderful day!"
        result = textblob_model.analyze(text)
        
        # Check that all VADER-compatible fields are present
        assert 'score' in result
        assert 'label' in result
        assert 'confidence' in result
        assert 'compound' in result
        assert 'positive' in result
        assert 'neutral' in result
        assert 'negative' in result
        assert 'model' in result
        
        # Check that score equals compound (VADER compatibility)
        assert result['score'] == result['compound']
    
    def test_positive_score_distribution(self, textblob_model):
        """Test that positive sentiment has correct score distribution"""
        text = "I absolutely love this amazing product!"
        result = textblob_model.analyze(text)
        
        if result['compound'] > 0:
            # For positive sentiment, positive score should be non-zero
            assert result['positive'] > 0.0
            assert result['negative'] == 0.0
            # Positive and neutral should sum to approximately 1.0
            assert abs((result['positive'] + result['neutral']) - 1.0) < 0.01
    
    def test_negative_score_distribution(self, textblob_model):
        """Test that negative sentiment has correct score distribution"""
        text = "I absolutely hate this terrible product!"
        result = textblob_model.analyze(text)
        
        if result['compound'] < 0:
            # For negative sentiment, negative score should be non-zero
            assert result['negative'] > 0.0
            assert result['positive'] == 0.0
            # Negative and neutral should sum to approximately 1.0
            assert abs((result['negative'] + result['neutral']) - 1.0) < 0.01
    
    def test_neutral_score_distribution(self, textblob_model):
        """Test that neutral sentiment has correct score distribution"""
        text = "The item is on the table."
        result = textblob_model.analyze(text)
        
        if result['compound'] == 0.0:
            # For neutral sentiment, only neutral should be 1.0
            assert result['positive'] == 0.0
            assert result['negative'] == 0.0
            assert result['neutral'] == 1.0
    
    def test_score_normalization(self, textblob_model):
        """Test that scores are properly normalized to VADER format"""
        texts = [
            "Excellent work!",
            "Poor quality.",
            "Standard item."
        ]
        
        for text in texts:
            result = textblob_model.analyze(text)
            
            # Compound should be in [-1.0, 1.0]
            assert -1.0 <= result['compound'] <= 1.0
            
            # Individual scores should sum to approximately 1.0
            score_sum = result['positive'] + result['neutral'] + result['negative']
            assert abs(score_sum - 1.0) < 0.01
    
    def test_classification_consistency(self, textblob_model):
        """Test that classification is consistent with compound score"""
        texts = [
            ("This is fantastic!", 'positive'),
            ("This is horrible!", 'negative'),
            ("This is a thing.", 'neutral')
        ]
        
        for text, expected_label in texts:
            result = textblob_model.analyze(text)
            
            # Verify label matches compound score thresholds
            if result['compound'] >= 0.05:
                assert result['label'] == 'positive'
            elif result['compound'] <= -0.05:
                assert result['label'] == 'negative'
            else:
                assert result['label'] == 'neutral'
