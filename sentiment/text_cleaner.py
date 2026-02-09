"""
Text Cleaner Module

This module provides utilities for cleaning and preprocessing text data
before sentiment analysis.
"""

import re


class TextCleaner:
    """Text preprocessing utilities for sentiment analysis"""
    
    @staticmethod
    def remove_urls(text: str) -> str:
        """
        Remove URLs from text.
        
        Args:
            text: Input text that may contain URLs
            
        Returns:
            Text with URLs removed
        """
        # Pattern to match http://, https://, and www. URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        text = re.sub(url_pattern, '', text)
        
        # Pattern to match www. URLs
        www_pattern = r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        text = re.sub(www_pattern, '', text)
        
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace to single spaces.
        
        Args:
            text: Input text with potentially irregular whitespace
            
        Returns:
            Text with normalized whitespace
        """
        # Replace multiple whitespace characters with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading and trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def clean(text: str) -> str:
        """
        Clean text by applying all cleaning steps.
        
        This method applies URL removal and whitespace normalization.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text ready for sentiment analysis
        """
        if not text:
            return ""
        
        # Apply all cleaning steps
        text = TextCleaner.remove_urls(text)
        text = TextCleaner.normalize_whitespace(text)
        
        return text
