"""
TextBlob Sentiment Analysis Model

This module implements sentiment analysis using the TextBlob library,
which provides a simple API for common natural language processing tasks.
"""

from textblob import TextBlob


class TextBlobModel:
    """
    TextBlob sentiment analysis implementation.
    
    TextBlob provides a simpler API for sentiment analysis and is good
    for general text. Scores are normalized to match VADER format for
    consistency across models.
    """
    
    def __init__(self):
        """Initialize TextBlob analyzer"""
        # TextBlob doesn't require explicit initialization
        pass
    
    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of text and return scores with label.
        
        TextBlob returns polarity in range [-1.0, 1.0] and subjectivity
        in range [0.0, 1.0]. We normalize these to match VADER format.
        
        Classification thresholds (matching VADER):
        - Positive: compound score >= 0.05
        - Negative: compound score <= -0.05
        - Neutral: -0.05 < compound score < 0.05
        
        Args:
            text: Text to analyze for sentiment
            
        Returns:
            Dictionary containing:
                - score: compound score (normalized polarity)
                - label: 'positive', 'negative', or 'neutral'
                - confidence: absolute value of compound score
                - compound: normalized polarity score [-1.0 to 1.0]
                - positive: normalized positive score [0.0 to 1.0]
                - neutral: normalized neutral score [0.0 to 1.0]
                - negative: normalized negative score [0.0 to 1.0]
                - model: 'textblob'
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
                'model': 'textblob'
            }
        
        # Get TextBlob sentiment
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # Range: [-1.0, 1.0]
        
        # Use polarity as compound score (already in correct range)
        compound = polarity
        
        # Classify based on compound score thresholds (matching VADER)
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Confidence is the absolute value of compound score
        confidence = abs(compound)
        
        # Normalize to VADER-like format with positive, neutral, negative scores
        # TextBlob doesn't provide these directly, so we derive them from polarity
        if compound > 0:
            # Positive sentiment
            positive = abs(compound)
            negative = 0.0
            neutral = 1.0 - positive
        elif compound < 0:
            # Negative sentiment
            negative = abs(compound)
            positive = 0.0
            neutral = 1.0 - negative
        else:
            # Neutral sentiment
            positive = 0.0
            negative = 0.0
            neutral = 1.0
        
        return {
            'score': compound,
            'label': label,
            'confidence': confidence,
            'compound': compound,
            'positive': positive,
            'neutral': neutral,
            'negative': negative,
            'model': 'textblob'
        }
