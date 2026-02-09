"""
Sentiment Analyzer Module

This module provides the main orchestrator for sentiment analysis,
handling file I/O, batch processing, and coordination with sentiment models.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from sentiment.text_cleaner import TextCleaner


logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Main sentiment analysis orchestrator.
    
    This class handles reading input data, processing text through
    sentiment models, and writing enriched output data.
    """
    
    def __init__(self, model_type: str = "vader", batch_size: int = 100):
        """
        Initialize sentiment analyzer.
        
        Args:
            model_type: Type of sentiment model to use ('vader' or 'textblob')
            batch_size: Number of texts to process in each batch
            
        Raises:
            ValueError: If model_type is not supported
        """
        self.model_type = model_type.lower()
        self.batch_size = batch_size
        self.text_cleaner = TextCleaner()
        
        # Model will be initialized lazily when needed
        self._model = None
        
        if self.model_type not in ['vader', 'textblob']:
            raise ValueError(f"Unsupported model type: {model_type}. Use 'vader' or 'textblob'.")
        
        logger.info(f"Initialized SentimentAnalyzer with model={model_type}, batch_size={batch_size}")
    
    @property
    def model(self):
        """Lazy initialization of sentiment model"""
        if self._model is None:
            if self.model_type == 'vader':
                from sentiment.models.vader_model import VADERModel
                self._model = VADERModel()
            elif self.model_type == 'textblob':
                from sentiment.models.textblob_model import TextBlobModel
                self._model = TextBlobModel()
        return self._model
    
    def analyze_file(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Analyze sentiment from input file and write to output file.
        
        Args:
            input_path: Path to input JSON file with posts
            output_path: Path to output JSON file with sentiment data
            
        Returns:
            Dictionary with processing statistics
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            json.JSONDecodeError: If input file is not valid JSON
            IOError: If output file cannot be written
        """
        logger.info(f"Starting sentiment analysis: input={input_path}, output={output_path}")
        
        # Read input file
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate input structure
        if 'posts' not in data:
            raise ValueError("Input JSON must contain 'posts' array")
        
        posts = data['posts']
        logger.info(f"Loaded {len(posts)} posts from input file")
        
        # Process posts in batches
        processed_posts = []
        error_count = 0
        
        for i in range(0, len(posts), self.batch_size):
            batch = posts[i:i + self.batch_size]
            logger.debug(f"Processing batch {i // self.batch_size + 1}: {len(batch)} posts")
            
            for post in batch:
                try:
                    # Analyze sentiment for this post
                    enriched_post = self._analyze_post(post)
                    processed_posts.append(enriched_post)
                except Exception as e:
                    logger.error(f"Error analyzing post {post.get('post_id', 'unknown')}: {e}")
                    error_count += 1
                    # Continue processing remaining posts
        
        # Update metadata
        if 'metadata' not in data:
            data['metadata'] = {}
        
        data['metadata']['analyzed_at'] = self._get_timestamp()
        data['metadata']['sentiment_model'] = self.model_type
        data['metadata']['total_posts'] = len(processed_posts)
        data['metadata']['error_count'] = error_count
        
        # Replace posts with processed posts
        data['posts'] = processed_posts
        
        # Write output file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Sentiment analysis complete: {len(processed_posts)} posts processed, {error_count} errors")
        
        return {
            'total_posts': len(processed_posts),
            'error_count': error_count,
            'model': self.model_type
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for a batch of texts.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of sentiment dictionaries
        """
        results = []
        
        for text in texts:
            try:
                result = self.analyze_single(text)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing text: {e}")
                # Return neutral sentiment as fallback
                results.append({
                    'score': 0.0,
                    'label': 'neutral',
                    'confidence': 0.0,
                    'compound': 0.0,
                    'positive': 0.0,
                    'neutral': 1.0,
                    'negative': 0.0,
                    'error': str(e)
                })
        
        return results
    
    def analyze_single(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment for a single text.
        
        Args:
            text: Text string to analyze
            
        Returns:
            Dictionary with sentiment scores and label
        """
        # Clean the text
        cleaned_text = self.text_cleaner.clean(text)
        
        # Analyze sentiment using the model
        sentiment = self.model.analyze(cleaned_text)
        
        return sentiment
    
    def _analyze_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment for a single post and enrich with sentiment data.
        Also analyzes comments if present.

        Args:
            post: Post dictionary with 'content' field and optional 'comments' array

        Returns:
            Enriched post dictionary with sentiment data for post and comments
        """
        # Create a copy to avoid modifying original
        enriched_post = post.copy()

        # Get content to analyze
        content = post.get('content', '')

        if not content:
            logger.warning(f"Post {post.get('post_id', 'unknown')} has no content")
            # Assign neutral sentiment for empty content
            enriched_post['sentiment'] = {
                'score': 0.0,
                'label': 'neutral',
                'confidence': 0.0,
                'compound': 0.0,
                'positive': 0.0,
                'neutral': 1.0,
                'negative': 0.0
            }
        else:
            # Analyze sentiment for post content
            sentiment = self.analyze_single(content)
            enriched_post['sentiment'] = sentiment

        # Analyze comments if present
        if 'comments' in post and isinstance(post['comments'], list):
            enriched_comments = []
            comment_sentiments = []

            for comment in post['comments']:
                try:
                    enriched_comment = comment.copy()
                    comment_text = comment.get('text', '')

                    if comment_text:
                        # Analyze comment sentiment
                        comment_sentiment = self.analyze_single(comment_text)
                        enriched_comment['sentiment'] = comment_sentiment
                        comment_sentiments.append(comment_sentiment)
                    else:
                        # Empty comment gets neutral sentiment
                        enriched_comment['sentiment'] = {
                            'score': 0.0,
                            'label': 'neutral',
                            'confidence': 0.0,
                            'compound': 0.0,
                            'positive': 0.0,
                            'neutral': 1.0,
                            'negative': 0.0
                        }

                    enriched_comments.append(enriched_comment)

                except Exception as e:
                    logger.error(f"Error analyzing comment: {e}")
                    enriched_comments.append(comment)

            enriched_post['comments'] = enriched_comments

            # Calculate aggregate sentiment statistics for comments
            if comment_sentiments:
                avg_compound = sum(s.get('compound', 0) for s in comment_sentiments) / len(comment_sentiments)
                avg_positive = sum(s.get('positive', 0) for s in comment_sentiments) / len(comment_sentiments)
                avg_neutral = sum(s.get('neutral', 0) for s in comment_sentiments) / len(comment_sentiments)
                avg_negative = sum(s.get('negative', 0) for s in comment_sentiments) / len(comment_sentiments)

                # Count sentiment labels
                positive_count = sum(1 for s in comment_sentiments if s.get('label') == 'positive')
                neutral_count = sum(1 for s in comment_sentiments if s.get('label') == 'neutral')
                negative_count = sum(1 for s in comment_sentiments if s.get('label') == 'negative')

                enriched_post['comments_sentiment_summary'] = {
                    'total_comments': len(comment_sentiments),
                    'average_compound': round(avg_compound, 3),
                    'average_positive': round(avg_positive, 3),
                    'average_neutral': round(avg_neutral, 3),
                    'average_negative': round(avg_negative, 3),
                    'positive_count': positive_count,
                    'neutral_count': neutral_count,
                    'negative_count': negative_count,
                    'positive_ratio': round(positive_count / len(comment_sentiments), 3) if comment_sentiments else 0,
                    'negative_ratio': round(negative_count / len(comment_sentiments), 3) if comment_sentiments else 0
                }

                logger.debug(f"Post {post.get('post_id', 'unknown')}: Analyzed {len(comment_sentiments)} comments")

        return enriched_post
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
