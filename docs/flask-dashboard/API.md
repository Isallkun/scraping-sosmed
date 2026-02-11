# API Documentation

This document describes the RESTful API endpoints provided by the Flask Analytics Dashboard.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Summary Statistics](#summary-statistics)
  - [Sentiment Analysis](#sentiment-analysis)
  - [Engagement Metrics](#engagement-metrics)
  - [Content Analysis](#content-analysis)
  - [Posts Data](#posts-data)
  - [Export Data](#export-data)
- [Query Parameters](#query-parameters)
- [Examples](#examples)

## Overview

The Flask Analytics Dashboard provides a RESTful API for programmatic access to Instagram analytics data. All endpoints return JSON responses and support CORS for cross-origin requests.

## Base URL

```
http://localhost:5000/api
```

For production deployments, replace `localhost:5000` with your server address.

## Authentication

Currently, the API does not require authentication. For production deployments, consider implementing:
- API keys
- OAuth 2.0
- JWT tokens

## Response Format

All API responses follow a consistent JSON format:

### Success Response

```json
{
  "data": { ... },
  "status": "success"
}
```

### Error Response

```json
{
  "error": "Error message",
  "status": 400,
  "timestamp": "2024-02-10T15:30:00Z"
}
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Database connection failed |

### Error Response Format

```json
{
  "error": "Invalid date format for start_date parameter",
  "status": 400,
  "timestamp": "2024-02-10T15:30:00Z"
}
```

## Endpoints

### Summary Statistics

Get overall statistics and key metrics.

**Endpoint**: `GET /api/summary`

**Description**: Returns total posts, comments, average sentiment, and post type distribution.

**Parameters**: None

**Response**:

```json
{
  "total_posts": 150,
  "total_comments": 1250,
  "avg_sentiment": 0.234,
  "last_execution": "2024-02-10T14:30:00Z",
  "post_type_distribution": {
    "post": 85,
    "reel": 65
  }
}
```

**Example**:

```bash
curl http://localhost:5000/api/summary
```

---

### Sentiment Analysis

Get sentiment distribution and trends.

**Endpoint**: `GET /api/sentiment`

**Description**: Returns sentiment distribution, trends over time, and average sentiment score.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Start date (ISO 8601 format) |
| `end_date` | string | No | End date (ISO 8601 format) |

**Response**:

```json
{
  "distribution": {
    "positive": 75,
    "neutral": 50,
    "negative": 25
  },
  "trends": [
    {
      "date": "2024-02-01",
      "score": 0.15
    },
    {
      "date": "2024-02-02",
      "score": 0.23
    }
  ],
  "gauge": 0.18
}
```

**Example**:

```bash
# All data
curl http://localhost:5000/api/sentiment

# Filtered by date range
curl "http://localhost:5000/api/sentiment?start_date=2024-02-01&end_date=2024-02-10"
```

---

### Engagement Metrics

Get engagement metrics and top posts.

**Endpoint**: `GET /api/engagement`

**Description**: Returns top posts by engagement rate, engagement trends, and post type distribution.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Start date (ISO 8601 format) |
| `end_date` | string | No | End date (ISO 8601 format) |
| `limit` | integer | No | Number of top posts (default: 10) |

**Response**:

```json
{
  "top_posts": [
    {
      "post_id": "ABC123",
      "author": "user123",
      "caption": "Amazing sunset...",
      "likes": 1500,
      "comments": 250,
      "engagement_rate": 12.5,
      "timestamp": "2024-02-10T12:00:00Z"
    }
  ],
  "trends": [
    {
      "date": "2024-02-01",
      "engagement_rate": 8.5
    }
  ],
  "type_distribution": {
    "post": 85,
    "reel": 65
  }
}
```

**Example**:

```bash
# Top 10 posts
curl http://localhost:5000/api/engagement

# Top 20 posts with date filter
curl "http://localhost:5000/api/engagement?limit=20&start_date=2024-02-01"
```

---

### Content Analysis

Get content analysis data (hashtags, posting patterns, content length).

**Endpoint**: `GET /api/content`

**Description**: Returns top hashtags, posting time heatmap, and content length distribution.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Start date (ISO 8601 format) |
| `end_date` | string | No | End date (ISO 8601 format) |

**Response**:

```json
{
  "hashtags": [
    {
      "hashtag": "instagram",
      "count": 45
    },
    {
      "hashtag": "photography",
      "count": 32
    }
  ],
  "posting_heatmap": [
    {
      "day_of_week": 1,
      "hour": 14,
      "count": 25
    }
  ],
  "length_distribution": [
    {
      "bin": "0-50",
      "count": 20
    },
    {
      "bin": "51-100",
      "count": 35
    }
  ]
}
```

**Example**:

```bash
curl http://localhost:5000/api/content
```

---

### Posts Data

Get paginated posts with search and filters.

**Endpoint**: `GET /api/posts`

**Description**: Returns paginated list of posts with optional search and filters.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number (default: 1) |
| `per_page` | integer | No | Results per page (default: 25) |
| `search` | string | No | Search term (searches caption and author) |
| `start_date` | string | No | Start date filter |
| `end_date` | string | No | End date filter |
| `post_type` | string | No | Post type filter (post, reel) |
| `sentiment` | string | No | Sentiment filter (positive, neutral, negative) |
| `sort_by` | string | No | Sort column (default: timestamp) |
| `sort_order` | string | No | Sort order: asc or desc (default: desc) |

**Response**:

```json
{
  "posts": [
    {
      "id": 1,
      "post_id": "ABC123",
      "author": "user123",
      "content": "Amazing sunset at the beach...",
      "timestamp": "2024-02-10T12:00:00Z",
      "likes": 1500,
      "comments_count": 250,
      "media_type": "post",
      "url": "https://instagram.com/p/ABC123",
      "score": 0.45,
      "label": "positive"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 25,
  "total_pages": 6
}
```

**Example**:

```bash
# First page, 25 results
curl http://localhost:5000/api/posts

# Page 2, 50 results
curl "http://localhost:5000/api/posts?page=2&per_page=50"

# Search for "coffee"
curl "http://localhost:5000/api/posts?search=coffee"

# Filter by post type and sentiment
curl "http://localhost:5000/api/posts?post_type=reel&sentiment=positive"

# Sort by likes (descending)
curl "http://localhost:5000/api/posts?sort_by=likes&sort_order=desc"
```

---

### Export Data

Export filtered posts to CSV.

**Endpoint**: `GET /api/export`

**Description**: Generates and downloads a CSV file of filtered posts.

**Parameters**:

Same as `/api/posts` endpoint (search, filters, sorting).

**Response**:

CSV file download with headers:
```
post_id,author,content,timestamp,likes,comments_count,sentiment_score,sentiment_label
```

**Example**:

```bash
# Export all posts
curl -O http://localhost:5000/api/export

# Export filtered posts
curl -O "http://localhost:5000/api/export?start_date=2024-02-01&sentiment=positive"
```

## Query Parameters

### Date Format

All date parameters should use ISO 8601 format:

```
YYYY-MM-DD
YYYY-MM-DDTHH:MM:SSZ
```

**Examples**:
- `2024-02-10`
- `2024-02-10T15:30:00Z`

### Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `per_page` | integer | 25 | Results per page (max: 100) |

### Sorting

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sort_by` | string | timestamp | Column to sort by |
| `sort_order` | string | desc | Sort order (asc, desc) |

**Valid sort_by values**:
- `timestamp`
- `likes`
- `comments_count`
- `shares`
- `author`
- `platform`
- `media_type`
- `score` (sentiment score)
- `label` (sentiment label)

### Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start of date range (inclusive) |
| `end_date` | string | End of date range (inclusive) |
| `post_type` | string | Filter by post or reel |
| `sentiment` | string | Filter by positive, neutral, or negative |
| `search` | string | Search term (case-insensitive) |

## Examples

### Python

```python
import requests

# Get summary statistics
response = requests.get('http://localhost:5000/api/summary')
data = response.json()
print(f"Total posts: {data['total_posts']}")

# Get sentiment data with date filter
params = {
    'start_date': '2024-02-01',
    'end_date': '2024-02-10'
}
response = requests.get('http://localhost:5000/api/sentiment', params=params)
sentiment_data = response.json()

# Search posts
params = {
    'search': 'coffee',
    'page': 1,
    'per_page': 50
}
response = requests.get('http://localhost:5000/api/posts', params=params)
posts = response.json()
```

### JavaScript (Fetch API)

```javascript
// Get summary statistics
fetch('http://localhost:5000/api/summary')
  .then(response => response.json())
  .then(data => {
    console.log('Total posts:', data.total_posts);
  });

// Get sentiment data with date filter
const params = new URLSearchParams({
  start_date: '2024-02-01',
  end_date: '2024-02-10'
});

fetch(`http://localhost:5000/api/sentiment?${params}`)
  .then(response => response.json())
  .then(data => {
    console.log('Sentiment distribution:', data.distribution);
  });

// Search posts
const searchParams = new URLSearchParams({
  search: 'coffee',
  page: 1,
  per_page: 50
});

fetch(`http://localhost:5000/api/posts?${searchParams}`)
  .then(response => response.json())
  .then(data => {
    console.log('Found posts:', data.posts.length);
  });
```

### cURL

```bash
# Get summary
curl http://localhost:5000/api/summary

# Get sentiment with date filter
curl "http://localhost:5000/api/sentiment?start_date=2024-02-01&end_date=2024-02-10"

# Search posts
curl "http://localhost:5000/api/posts?search=coffee&page=1&per_page=50"

# Get top engagement posts
curl "http://localhost:5000/api/engagement?limit=20"

# Export filtered data
curl -O "http://localhost:5000/api/export?sentiment=positive&start_date=2024-02-01"
```

## Rate Limiting

Currently, there is no rate limiting implemented. For production deployments, consider implementing rate limiting to prevent abuse.

## CORS

All API endpoints support Cross-Origin Resource Sharing (CORS) and can be accessed from any origin.

## Caching

API responses are cached for 5 minutes (configurable via `CACHE_DEFAULT_TIMEOUT` environment variable). To bypass cache, restart the Flask application or import new data (which invalidates the cache).

## Versioning

The current API version is v1. Future versions may be introduced with a `/api/v2/` prefix.

## Support

For API issues or questions:

1. Check application logs in `logs/flask_dashboard.log`
2. Review the [Troubleshooting Guide](TROUBLESHOOTING.md)
3. Verify database connection and data availability

## Future Enhancements

Planned API enhancements:

- Authentication and authorization
- Rate limiting
- Webhooks for real-time updates
- Batch operations
- GraphQL endpoint
- API versioning
