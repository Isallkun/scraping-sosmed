"""
Utility functions for data transformation and analysis.

This module provides helper functions for sentiment classification,
engagement rate calculation, and hashtag extraction.
"""

import re
from typing import List


def classify_sentiment(score: float) -> str:
    """
    Classify sentiment score into category.
    
    Args:
        score: Sentiment score value (typically between -1.0 and 1.0)
        
    Returns:
        str: Sentiment category - 'positive', 'neutral', or 'negative'
        
    Classification rules:
        - positive: score > 0.05
        - neutral: -0.05 <= score <= 0.05
        - negative: score < -0.05
        
    Examples:
        >>> classify_sentiment(0.8)
        'positive'
        >>> classify_sentiment(0.02)
        'neutral'
        >>> classify_sentiment(-0.3)
        'negative'
    """
    if score > 0.05:
        return 'positive'
    elif score < -0.05:
        return 'negative'
    else:
        return 'neutral'


def calculate_engagement_rate(likes: int, comments: int, followers: int) -> float:
    """
    Calculate engagement rate as percentage.
    
    Args:
        likes: Number of likes on the post
        comments: Number of comments on the post
        followers: Number of followers the account has
        
    Returns:
        float: Engagement rate as a percentage (0.0 if followers is 0)
        
    Formula:
        engagement_rate = ((likes + comments) / followers) * 100
        
    Examples:
        >>> calculate_engagement_rate(100, 50, 1000)
        15.0
        >>> calculate_engagement_rate(10, 5, 0)
        0.0
    """
    if followers == 0:
        return 0.0
    return ((likes + comments) / followers) * 100


def extract_hashtags(caption: str) -> List[str]:
    """
    Extract hashtags from caption text.
    
    Args:
        caption: Post caption text containing hashtags
        
    Returns:
        List[str]: List of hashtags (without the # symbol) in order of appearance
        
    Pattern:
        Matches hashtags in the format #word where word consists of alphanumeric
        characters and underscores.
        
    Examples:
        >>> extract_hashtags("Love this! #python #coding #dev")
        ['python', 'coding', 'dev']
        >>> extract_hashtags("No hashtags here")
        []
        >>> extract_hashtags("#first #second #first")
        ['first', 'second', 'first']
    """
    return re.findall(r'#(\w+)', caption)
