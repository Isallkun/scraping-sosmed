"""
VADER Sentiment Analysis Model

This module implements sentiment analysis using the VADER
(Valence Aware Dictionary and sEntiment Reasoner) model,
which is specifically optimized for social media text.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class VADERModel:
    """
    VADER sentiment analysis implementation.
    
    VADER is optimized for social media sentiment analysis and handles
    emojis, slang, and informal language effectively.
    """
    
    def __init__(self):
        """Initialize VADER SentimentIntensityAnalyzer"""
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of text and return scores with label.
        
        Classification thresholds:
        - Positive: compound score >= 0.05
        - Negative: compound score <= -0.05
        - Neutral: -0.05 < compound score < 0.05
        
        Args:
            text: Text to analyze for sentiment
            
        Returns:
            Dictionary containing:
                - score: compound score (same as compound)
                - label: 'positive', 'negative', or 'neutral'
                - confidence: absolute value of compound score
                - compound: VADER compound score [-1.0 to 1.0]
                - positive: positive score [0.0 to 1.0]
                - neutral: neutral score [0.0 to 1.0]
                - negative: negative score [0.0 to 1.0]
                - model: 'vader'
        """
        if not text or not text.strip():
            # Return neutral sentiment for empty text
            return {
                'score': 0.0,
                'label': 'neutral',
                'confidence': 0.0,
                'compound': 0.0,
                'positive': 0.0,
                'neutral': 1.0,
                'negative': 0.0,
                'model': 'vader'
            }
        
        # Get VADER scores
        scores = self.analyzer.polarity_scores(text)
        
        # Extract compound score
        compound = scores['compound']
        
        # Classify based on compound score thresholds
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Confidence is the absolute value of compound score
        confidence = abs(compound)
        
        return {
            'score': compound,
            'label': label,
            'confidence': confidence,
            'compound': compound,
            'positive': scores['pos'],
            'neutral': scores['neu'],
            'negative': scores['neg'],
            'model': 'vader'
        }
