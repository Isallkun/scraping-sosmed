# Utility Functions Documentation

## Overview

The `app/services/utils.py` module provides utility functions for data transformation and analysis in the Flask Analytics Dashboard. These functions are used throughout the application for sentiment classification, engagement rate calculation, and hashtag extraction.

## Functions

### 1. classify_sentiment(score: float) -> str

Classifies a sentiment score into one of three categories: positive, neutral, or negative.

**Parameters:**
- `score` (float): Sentiment score value (typically between -1.0 and 1.0)

**Returns:**
- `str`: Sentiment category - 'positive', 'neutral', or 'negative'

**Classification Rules:**
- **positive**: score > 0.05
- **neutral**: -0.05 ≤ score ≤ 0.05
- **negative**: score < -0.05

**Examples:**
```python
classify_sentiment(0.8)    # Returns: 'positive'
classify_sentiment(0.02)   # Returns: 'neutral'
classify_sentiment(-0.3)   # Returns: 'negative'
```

**Validates:** Requirements 4.5

---

### 2. calculate_engagement_rate(likes: int, comments: int, followers: int) -> float

Calculates the engagement rate as a percentage based on likes, comments, and follower count.

**Parameters:**
- `likes` (int): Number of likes on the post
- `comments` (int): Number of comments on the post
- `followers` (int): Number of followers the account has

**Returns:**
- `float`: Engagement rate as a percentage (0.0 if followers is 0)

**Formula:**
```
engagement_rate = ((likes + comments) / followers) * 100
```

**Examples:**
```python
calculate_engagement_rate(100, 50, 1000)  # Returns: 15.0
calculate_engagement_rate(10, 5, 0)       # Returns: 0.0 (avoids division by zero)
```

**Validates:** Requirements 5.5

---

### 3. extract_hashtags(caption: str) -> List[str]

Extracts all hashtags from a caption text using regex pattern matching.

**Parameters:**
- `caption` (str): Post caption text containing hashtags

**Returns:**
- `List[str]`: List of hashtags (without the # symbol) in order of appearance

**Pattern:**
Matches hashtags in the format `#word` where word consists of alphanumeric characters and underscores (`\w+`).

**Examples:**
```python
extract_hashtags("Love this! #python #coding #dev")
# Returns: ['python', 'coding', 'dev']

extract_hashtags("No hashtags here")
# Returns: []

extract_hashtags("#first #second #first")
# Returns: ['first', 'second', 'first']  # Duplicates preserved
```

**Validates:** Requirements 6.5

---

## Usage in the Application

These utility functions are imported and used in:

1. **app/services/data_service.py**: 
   - `extract_hashtags()` is used in `get_content_data()` to extract hashtags from post captions
   - `classify_sentiment()` can be used for sentiment classification in data transformations
   - `calculate_engagement_rate()` can be used for engagement metrics calculations

2. **Future API endpoints and templates**: These functions provide consistent data transformation across the application

## Testing

Comprehensive unit tests are available in `tests/test_utils.py` covering:

- **Sentiment Classification**: 8 test cases covering boundaries, edge cases, and typical values
- **Engagement Rate Calculation**: 9 test cases covering zero followers, high/low engagement, and edge cases
- **Hashtag Extraction**: 12 test cases covering various caption formats, special characters, and edge cases

**Run tests:**
```bash
python -m pytest tests/test_utils.py -v
```

All 29 tests pass successfully.

## Implementation Notes

1. **Sentiment Classification**: Uses threshold values of ±0.05 to define neutral sentiment range, as specified in Requirement 4.5
2. **Engagement Rate**: Returns 0.0 when followers is 0 to avoid division by zero errors
3. **Hashtag Extraction**: Uses regex pattern `#(\w+)` which matches hashtags with alphanumeric characters and underscores, stopping at special characters or spaces

## Requirements Validation

- ✅ **Requirement 4.5**: Sentiment classification with thresholds (positive > 0.05, neutral -0.05 to 0.05, negative < -0.05)
- ✅ **Requirement 5.5**: Engagement rate calculation as (likes + comments) / followers
- ✅ **Requirement 6.5**: Hashtag extraction using regex pattern matching
