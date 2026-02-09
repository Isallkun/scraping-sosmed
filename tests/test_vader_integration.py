"""
Integration tests for VADER model with text cleaning.

Tests the integration between TextCleaner and VADERModel to ensure
they work together correctly for sentiment analysis.
"""

import pytest
from sentiment.models.vader_model import VADERModel
from sentiment.text_cleaner import TextCleaner


class TestVADERIntegration:
    """Test suite for VADER model integration with text cleaning"""
    
    @pytest.fixture
    def vader_model(self):
        """Create a VADERModel instance for testing"""
        return VADERModel()
    
    def test_analyze_with_cleaned_text(self, vader_model):
        """Test that VADER works with cleaned text"""
        # Text with URLs and extra whitespace
        dirty_text = "I love this product!   https://example.com   It's amazing!"
        
        # Clean the text
        clean_text = TextCleaner.clean(dirty_text)
        
        # Analyze cleaned text
        result = vader_model.analyze(clean_text)
        
        assert result['label'] == 'positive'
        assert result['compound'] > 0
        assert result['model'] == 'vader'
    
    def test_analyze_text_with_urls_removed(self, vader_model):
        """Test sentiment analysis after URL removal"""
        text_with_url = "Check out this great site www.example.com it's awesome!"
        clean_text = TextCleaner.remove_urls(text_with_url)
        
        result = vader_model.analyze(clean_text)
        
        # Should still detect positive sentiment
        assert result['label'] in ['positive', 'neutral']
        assert result['compound'] >= 0
    
    def test_analyze_text_with_normalized_whitespace(self, vader_model):
        """Test sentiment analysis after whitespace normalization"""
        text_with_spaces = "This    is     great!    Really    love    it!"
        clean_text = TextCleaner.normalize_whitespace(text_with_spaces)
        
        result = vader_model.analyze(clean_text)
        
        assert result['label'] == 'positive'
        assert result['compound'] > 0
    
    def test_full_cleaning_pipeline(self, vader_model):
        """Test complete cleaning and analysis pipeline"""
        # Realistic social media post with URLs and irregular spacing
        raw_text = """
        Just bought this product from https://store.com and I'm so happy!  
        Best purchase ever!!!   😊
        Check it out at www.store.com/product
        """
        
        # Clean the text
        clean_text = TextCleaner.clean(raw_text)
        
        # Analyze sentiment
        result = vader_model.analyze(clean_text)
        
        # Should detect positive sentiment
        assert result['label'] == 'positive'
        assert result['compound'] > 0
        assert 'score' in result
        assert 'confidence' in result
    
    def test_empty_after_cleaning(self, vader_model):
        """Test handling of text that becomes empty after cleaning"""
        # Text that only contains URLs
        url_only_text = "https://example.com www.test.com"
        clean_text = TextCleaner.clean(url_only_text)
        
        result = vader_model.analyze(clean_text)
        
        # Should return neutral for empty text
        assert result['label'] == 'neutral'
        assert result['compound'] == 0.0
    
    def test_negative_sentiment_preserved_after_cleaning(self, vader_model):
        """Test that negative sentiment is preserved after cleaning"""
        text = "This is terrible!   https://example.com   Worst experience ever!"
        clean_text = TextCleaner.clean(text)
        
        result = vader_model.analyze(clean_text)
        
        assert result['label'] == 'negative'
        assert result['compound'] < 0
