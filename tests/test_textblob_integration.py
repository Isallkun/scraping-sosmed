"""
Integration tests for TextBlob sentiment model with SentimentAnalyzer.

Tests the integration of TextBlobModel with the SentimentAnalyzer
to ensure proper end-to-end functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from sentiment.sentiment_analyzer import SentimentAnalyzer


class TestTextBlobIntegration:
    """Test suite for TextBlob integration with SentimentAnalyzer"""
    
    @pytest.fixture
    def sample_posts_data(self):
        """Create sample posts data for testing"""
        return {
            "metadata": {
                "platform": "instagram",
                "scraped_at": "2024-01-15T10:30:00Z",
                "total_posts": 3
            },
            "posts": [
                {
                    "post_id": "post1",
                    "platform": "instagram",
                    "author": "user1",
                    "content": "I absolutely love this amazing product!",
                    "timestamp": "2024-01-14T15:20:00Z",
                    "likes": 150
                },
                {
                    "post_id": "post2",
                    "platform": "instagram",
                    "author": "user2",
                    "content": "This is terrible and disappointing.",
                    "timestamp": "2024-01-14T16:30:00Z",
                    "likes": 20
                },
                {
                    "post_id": "post3",
                    "platform": "instagram",
                    "author": "user3",
                    "content": "The item is on the table.",
                    "timestamp": "2024-01-14T17:45:00Z",
                    "likes": 50
                }
            ]
        }
    
    def test_textblob_analyzer_initialization(self):
        """Test that SentimentAnalyzer initializes with TextBlob model"""
        analyzer = SentimentAnalyzer(model_type="textblob")
        
        assert analyzer.model_type == "textblob"
        assert analyzer.model is not None
    
    def test_textblob_analyze_single(self):
        """Test single text analysis with TextBlob"""
        analyzer = SentimentAnalyzer(model_type="textblob")
        
        # Test positive text
        result = analyzer.analyze_single("I love this!")
        assert result['label'] in ['positive', 'neutral', 'negative']
        assert result['model'] == 'textblob'
        assert 'compound' in result
        assert 'confidence' in result
        
        # Test negative text
        result = analyzer.analyze_single("I hate this!")
        assert result['label'] in ['positive', 'neutral', 'negative']
        assert result['model'] == 'textblob'
    
    def test_textblob_analyze_batch(self):
        """Test batch text analysis with TextBlob"""
        analyzer = SentimentAnalyzer(model_type="textblob")
        
        texts = [
            "This is wonderful!",
            "This is awful!",
            "This is a thing."
        ]
        
        results = analyzer.analyze_batch(texts)
        
        assert len(results) == 3
        for result in results:
            assert 'label' in result
            assert 'compound' in result
            assert result['model'] == 'textblob'
    
    def test_textblob_analyze_file(self, sample_posts_data):
        """Test file analysis with TextBlob"""
        analyzer = SentimentAnalyzer(model_type="textblob")
        
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(sample_posts_data, f)
            input_path = f.name
        
        # Create temporary output file path
        output_path = tempfile.mktemp(suffix='.json')
        
        try:
            # Analyze file
            stats = analyzer.analyze_file(input_path, output_path)
            
            # Check statistics
            assert stats['total_posts'] == 3
            assert stats['error_count'] == 0
            assert stats['model'] == 'textblob'
            
            # Read output file
            with open(output_path, 'r', encoding='utf-8') as f:
                output_data = json.load(f)
            
            # Verify metadata
            assert output_data['metadata']['sentiment_model'] == 'textblob'
            assert output_data['metadata']['total_posts'] == 3
            assert 'analyzed_at' in output_data['metadata']
            
            # Verify posts have sentiment data
            assert len(output_data['posts']) == 3
            for post in output_data['posts']:
                assert 'sentiment' in post
                assert 'label' in post['sentiment']
                assert 'compound' in post['sentiment']
                assert 'confidence' in post['sentiment']
                assert post['sentiment']['model'] == 'textblob'
                
                # Verify original fields are preserved
                assert 'post_id' in post
                assert 'author' in post
                assert 'content' in post
                assert 'likes' in post
        
        finally:
            # Clean up temporary files
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)
    
    def test_textblob_empty_content(self):
        """Test TextBlob handling of empty content"""
        analyzer = SentimentAnalyzer(model_type="textblob")
        
        result = analyzer.analyze_single("")
        
        assert result['label'] == 'neutral'
        assert result['compound'] == 0.0
        assert result['model'] == 'textblob'
    
    def test_textblob_with_urls(self):
        """Test TextBlob with text containing URLs (should be cleaned)"""
        analyzer = SentimentAnalyzer(model_type="textblob")
        
        text = "Check out this amazing product at https://example.com!"
        result = analyzer.analyze_single(text)
        
        # Should analyze sentiment after URL removal
        assert result['label'] in ['positive', 'neutral', 'negative']
        assert result['model'] == 'textblob'
    
    def test_textblob_error_handling(self):
        """Test TextBlob error handling in batch processing"""
        analyzer = SentimentAnalyzer(model_type="textblob")
        
        # Mix of valid and potentially problematic texts
        texts = [
            "This is great!",
            "",  # Empty text
            "   ",  # Whitespace only
            "Normal text here."
        ]
        
        results = analyzer.analyze_batch(texts)
        
        # Should return results for all texts
        assert len(results) == 4
        for result in results:
            assert 'label' in result
            assert 'compound' in result
    
    def test_textblob_preserves_original_fields(self, sample_posts_data):
        """Test that TextBlob analysis preserves all original post fields"""
        analyzer = SentimentAnalyzer(model_type="textblob")
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(sample_posts_data, f)
            input_path = f.name
        
        output_path = tempfile.mktemp(suffix='.json')
        
        try:
            analyzer.analyze_file(input_path, output_path)
            
            # Read output
            with open(output_path, 'r', encoding='utf-8') as f:
                output_data = json.load(f)
            
            # Check that original fields are preserved
            for i, post in enumerate(output_data['posts']):
                original_post = sample_posts_data['posts'][i]
                
                # All original fields should be present
                assert post['post_id'] == original_post['post_id']
                assert post['platform'] == original_post['platform']
                assert post['author'] == original_post['author']
                assert post['content'] == original_post['content']
                assert post['timestamp'] == original_post['timestamp']
                assert post['likes'] == original_post['likes']
                
                # Sentiment field should be added
                assert 'sentiment' in post
        
        finally:
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)
    
    def test_textblob_vs_vader_format_compatibility(self):
        """Test that TextBlob output format is compatible with VADER format"""
        textblob_analyzer = SentimentAnalyzer(model_type="textblob")
        vader_analyzer = SentimentAnalyzer(model_type="vader")
        
        text = "This is a test sentence."
        
        textblob_result = textblob_analyzer.analyze_single(text)
        vader_result = vader_analyzer.analyze_single(text)
        
        # Both should have the same fields
        textblob_fields = set(textblob_result.keys())
        vader_fields = set(vader_result.keys())
        
        # Check that all required fields are present in both
        required_fields = {'score', 'label', 'confidence', 'compound', 
                          'positive', 'neutral', 'negative', 'model'}
        
        assert required_fields.issubset(textblob_fields)
        assert required_fields.issubset(vader_fields)
        
        # Model field should differ
        assert textblob_result['model'] == 'textblob'
        assert vader_result['model'] == 'vader'
