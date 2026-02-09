# Design Document: Social Media Scraper Automation

## Overview

Sistem ini adalah platform otomasi end-to-end untuk scraping data sosial media, analisis sentimen, dan reporting. Arsitektur menggunakan pendekatan microservices dengan komponen-komponen yang loosely coupled:

- **Selenium Scraper**: Python service untuk web scraping dengan anti-detection
- **Sentiment Analyzer**: Python module untuk analisis sentimen menggunakan VADER/TextBlob
- **n8n Workflows**: Orchestration layer untuk automasi dan scheduling
- **PostgreSQL Database**: Persistent storage untuk data dan logs
- **Docker Environment**: Containerized deployment untuk portability dan scalability

Sistem dirancang untuk production-ready dengan fokus pada reliability, maintainability, dan compliance dengan platform terms of service.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        n8n Workflows                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Daily Cron   │  │  On-Demand   │  │   Weekly     │      │
│  │   Workflow   │  │   Webhook    │  │   Report     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python Services Layer                     │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │  Selenium Scraper    │───▶│  Sentiment Analyzer  │      │
│  │  - Login automation  │    │  - Text cleaning     │      │
│  │  - Data extraction   │    │  - VADER/TextBlob    │      │
│  │  - Anti-detection    │    │  - Batch processing  │      │
│  │  - Rate limiting     │    │  - Score calculation │      │
│  └──────────┬───────────┘    └──────────┬───────────┘      │
└─────────────┼──────────────────────────┼─────────────────────┘
              │                          │
              ▼                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐          │
│  │  posts   │  │sentiments│  │ execution_logs   │          │
│  └──────────┘  └──────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│              Notification System (Email/Slack/Telegram)      │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

**Daily Scraping Flow:**
1. n8n Cron Trigger activates at scheduled time
2. n8n executes Python scraper via Execute Command node
3. Scraper authenticates, scrapes data, outputs JSON
4. n8n reads JSON output and passes to Sentiment Analyzer
5. Sentiment Analyzer processes data and outputs enriched JSON
6. n8n stores results to PostgreSQL
7. n8n generates summary and sends notification
8. n8n logs execution status to execution_logs table

**On-Demand Flow:**
1. HTTP webhook receives request with target parameters
2. n8n validates payload and extracts parameters
3. n8n executes scraper with custom parameters
4. Scraper returns results to n8n
5. n8n performs quick sentiment analysis
6. n8n returns JSON response via webhook
7. n8n logs execution metadata

### Technology Stack Rationale

- **Selenium WebDriver**: Handles JavaScript-heavy social media sites, supports authentication flows
- **Python 3.x**: Rich ecosystem for web scraping (BeautifulSoup, Selenium) and NLP (VADER, TextBlob)
- **n8n**: Open-source workflow automation with visual editor, extensive integrations, self-hostable
- **PostgreSQL**: Robust relational database with JSON support, good for structured data with relationships
- **Docker Compose**: Simplifies multi-container deployment, ensures consistency across environments
- **VADER**: Optimized for social media sentiment analysis, handles emojis and slang
- **TextBlob**: Alternative sentiment analyzer, simpler API, good for general text

## Components and Interfaces

### Component 1: Selenium Scraper

**Responsibility**: Authenticate to social media platforms and extract post data with anti-detection measures.

**Module Structure**:
```
scraper/
├── __init__.py
├── main_scraper.py       # Entry point and CLI
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py   # Abstract base class
│   ├── instagram.py      # Instagram-specific scraper
│   ├── twitter.py        # Twitter-specific scraper
│   └── facebook.py       # Facebook-specific scraper
├── utils/
│   ├── __init__.py
│   ├── anti_detection.py # User agents, delays, viewport
│   ├── rate_limiter.py   # Rate limiting logic
│   └── logger.py         # Logging configuration
└── config.py             # Configuration management
```

**Key Classes**:

```python
class BaseScraper:
    """Abstract base class for platform-specific scrapers"""
    
    def __init__(self, credentials: dict, config: dict):
        """Initialize scraper with credentials and configuration"""
        
    def authenticate(self) -> bool:
        """Authenticate to the platform"""
        
    def scrape_posts(self, target_url: str, limit: int) -> List[dict]:
        """Scrape posts from target URL"""
        
    def extract_post_data(self, post_element) -> dict:
        """Extract structured data from post element"""
        
    def apply_rate_limiting(self):
        """Apply rate limiting between requests"""
        
    def close(self):
        """Clean up resources"""

class AntiDetection:
    """Utilities for avoiding bot detection"""
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Return random user agent string"""
        
    @staticmethod
    def get_random_viewport() -> tuple:
        """Return random viewport dimensions"""
        
    @staticmethod
    def human_like_delay(min_sec: float, max_sec: float):
        """Sleep for random duration to mimic human behavior"""

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int):
        """Initialize with rate limit"""
        
    def acquire(self):
        """Block until request can proceed"""
        
    def reset(self):
        """Reset rate limiter"""
```

**CLI Interface**:
```bash
python main_scraper.py \
  --platform instagram \
  --target "https://instagram.com/username" \
  --limit 50 \
  --output posts.json \
  --format json
```

**Output Format** (JSON):
```json
{
  "metadata": {
    "platform": "instagram",
    "scraped_at": "2024-01-15T10:30:00Z",
    "target_url": "https://instagram.com/username",
    "total_posts": 50
  },
  "posts": [
    {
      "post_id": "abc123",
      "platform": "instagram",
      "author": "username",
      "author_id": "user123",
      "content": "Post caption text here",
      "timestamp": "2024-01-14T15:20:00Z",
      "likes": 150,
      "comments_count": 25,
      "shares": 10,
      "url": "https://instagram.com/p/abc123",
      "media_type": "image",
      "hashtags": ["tag1", "tag2"]
    }
  ]
}
```

**Configuration** (Environment Variables):
```
SCRAPER_PLATFORM=instagram
SCRAPER_USERNAME=your_username
SCRAPER_PASSWORD=your_password
SCRAPER_RATE_LIMIT=30
SCRAPER_MAX_POSTS=100
SCRAPER_TIMEOUT=300
SCRAPER_HEADLESS=true
SCRAPER_LOG_LEVEL=INFO
```

### Component 2: Sentiment Analyzer

**Responsibility**: Analyze sentiment of text content and enrich data with sentiment scores and labels.

**Module Structure**:
```
sentiment/
├── __init__.py
├── sentiment_analyzer.py  # Main analyzer class
├── text_cleaner.py        # Text preprocessing
├── models/
│   ├── __init__.py
│   ├── vader_model.py     # VADER implementation
│   └── textblob_model.py  # TextBlob implementation
└── config.py              # Sentiment thresholds
```

**Key Classes**:

```python
class SentimentAnalyzer:
    """Main sentiment analysis orchestrator"""
    
    def __init__(self, model_type: str = "vader", batch_size: int = 100):
        """Initialize with model type and batch size"""
        
    def analyze_file(self, input_path: str, output_path: str):
        """Analyze sentiment from input file and write to output"""
        
    def analyze_batch(self, texts: List[str]) -> List[dict]:
        """Analyze sentiment for batch of texts"""
        
    def analyze_single(self, text: str) -> dict:
        """Analyze sentiment for single text"""

class TextCleaner:
    """Text preprocessing utilities"""
    
    @staticmethod
    def clean(text: str) -> str:
        """Clean text by removing URLs, special chars, normalizing whitespace"""
        
    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text"""
        
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace to single spaces"""

class VADERModel:
    """VADER sentiment analysis implementation"""
    
    def __init__(self):
        """Initialize VADER analyzer"""
        
    def analyze(self, text: str) -> dict:
        """Return sentiment scores and label"""

class TextBlobModel:
    """TextBlob sentiment analysis implementation"""
    
    def __init__(self):
        """Initialize TextBlob analyzer"""
        
    def analyze(self, text: str) -> dict:
        """Return sentiment scores and label"""
```

**CLI Interface**:
```bash
python sentiment_analyzer.py \
  --input posts.json \
  --output posts_with_sentiment.json \
  --model vader \
  --batch-size 100
```

**Output Format** (Enriched JSON):
```json
{
  "metadata": {
    "platform": "instagram",
    "scraped_at": "2024-01-15T10:30:00Z",
    "analyzed_at": "2024-01-15T10:35:00Z",
    "total_posts": 50,
    "sentiment_model": "vader"
  },
  "posts": [
    {
      "post_id": "abc123",
      "platform": "instagram",
      "author": "username",
      "content": "Post caption text here",
      "timestamp": "2024-01-14T15:20:00Z",
      "likes": 150,
      "sentiment": {
        "score": 0.75,
        "label": "positive",
        "confidence": 0.85,
        "compound": 0.75,
        "positive": 0.8,
        "neutral": 0.15,
        "negative": 0.05
      }
    }
  ]
}
```

**Sentiment Classification Logic**:
- **Positive**: compound score >= 0.05
- **Neutral**: -0.05 < compound score < 0.05
- **Negative**: compound score <= -0.05

### Component 3: n8n Workflows

**Responsibility**: Orchestrate scraping, analysis, storage, and reporting workflows.

#### Workflow 1: Daily Scraping Workflow

**Trigger**: Cron (configurable, default: daily at 2 AM)

**Nodes**:
1. **Cron Trigger** - Schedule: `0 2 * * *`
2. **Execute Command** - Run scraper: `python main_scraper.py --platform instagram --limit 100 --output /tmp/posts.json`
3. **IF Error** - Check exit code
   - **True**: Send Error Alert (Email/Slack)
   - **False**: Continue
4. **Read Binary File** - Read `/tmp/posts.json`
5. **Execute Command** - Run sentiment analyzer: `python sentiment_analyzer.py --input /tmp/posts.json --output /tmp/posts_sentiment.json`
6. **Read Binary File** - Read `/tmp/posts_sentiment.json`
7. **JSON Parse** - Parse JSON data
8. **Split In Batches** - Process posts in batches of 50
9. **PostgreSQL Insert** - Insert into posts table
10. **PostgreSQL Insert** - Insert into sentiments table
11. **Aggregate** - Calculate daily summary (total posts, sentiment distribution)
12. **Send Email/Slack** - Send success notification with summary
13. **PostgreSQL Insert** - Log execution to execution_logs

**Error Handling**:
- Each critical node has error output connected to notification node
- Execution logs capture all errors with stack traces
- Workflow continues even if individual posts fail (logged as warnings)

#### Workflow 2: On-Demand Analysis Workflow

**Trigger**: Webhook - POST `/webhook/scrape`

**Request Payload**:
```json
{
  "platform": "instagram",
  "target_url": "https://instagram.com/username",
  "limit": 20
}
```

**Nodes**:
1. **Webhook Trigger** - Listen on `/webhook/scrape`
2. **Validate Payload** - Check required fields (platform, target_url)
3. **IF Invalid** - Return 400 error response
4. **Execute Command** - Run scraper with parameters from payload
5. **Read Binary File** - Read scraper output
6. **Execute Command** - Run sentiment analyzer
7. **Read Binary File** - Read analyzer output
8. **JSON Parse** - Parse results
9. **PostgreSQL Insert** - Store results (optional, based on payload flag)
10. **Respond to Webhook** - Return JSON response with results
11. **PostgreSQL Insert** - Log execution metadata

**Response Format**:
```json
{
  "status": "success",
  "data": {
    "total_posts": 20,
    "sentiment_summary": {
      "positive": 12,
      "neutral": 5,
      "negative": 3
    },
    "posts": [...]
  },
  "execution_time_ms": 15000
}
```

#### Workflow 3: Weekly Report Workflow

**Trigger**: Cron - Weekly (Sunday at 9 AM)

**Nodes**:
1. **Cron Trigger** - Schedule: `0 9 * * 0`
2. **PostgreSQL Query** - Get posts from last 7 days
3. **PostgreSQL Query** - Get sentiment data for those posts
4. **Aggregate** - Calculate metrics:
   - Total posts per day
   - Sentiment distribution over time
   - Top authors by engagement
   - Trending hashtags
5. **Function** - Generate chart data (JSON for visualization)
6. **HTTP Request** - Call chart generation service (e.g., QuickChart API)
7. **Merge** - Combine data and charts
8. **Function** - Format report as HTML/Markdown
9. **Convert to PDF** - Use Puppeteer or similar
10. **Send Email** - Send report to stakeholders with PDF attachment
11. **PostgreSQL Insert** - Log report generation

**Report Metrics**:
- Total posts scraped (7-day trend)
- Sentiment distribution (pie chart)
- Daily sentiment trend (line chart)
- Top 10 most engaged posts
- Platform comparison (if multi-platform)
- Error rate and system health

### Component 4: Database Schema

**Database**: PostgreSQL 14+

**Schema**:

```sql
-- Posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(255) UNIQUE NOT NULL,
    platform VARCHAR(50) NOT NULL,
    author VARCHAR(255) NOT NULL,
    author_id VARCHAR(255),
    content TEXT,
    timestamp TIMESTAMP NOT NULL,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    url TEXT,
    media_type VARCHAR(50),
    hashtags TEXT[],
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_platform ON posts(platform);
CREATE INDEX idx_posts_timestamp ON posts(timestamp);
CREATE INDEX idx_posts_author ON posts(author);
CREATE INDEX idx_posts_scraped_at ON posts(scraped_at);

-- Sentiments table
CREATE TABLE sentiments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    score DECIMAL(5,4) NOT NULL,
    label VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,4),
    compound DECIMAL(5,4),
    positive DECIMAL(5,4),
    neutral DECIMAL(5,4),
    negative DECIMAL(5,4),
    model VARCHAR(50) NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sentiments_post_id ON sentiments(post_id);
CREATE INDEX idx_sentiments_label ON sentiments(label);
CREATE INDEX idx_sentiments_processed_at ON sentiments(processed_at);

-- Execution logs table
CREATE TABLE execution_logs (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) NOT NULL,
    workflow_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    duration_ms INTEGER,
    error_message TEXT,
    error_stack TEXT,
    metadata JSONB,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_workflow_id ON execution_logs(workflow_id);
CREATE INDEX idx_logs_status ON execution_logs(status);
CREATE INDEX idx_logs_executed_at ON execution_logs(executed_at);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Data Retention Policy**:
- Posts older than 90 days: Archive to cold storage or delete
- Execution logs older than 30 days: Delete
- Sentiments: Retain as long as associated posts exist (CASCADE delete)

**Backup Strategy**:
- Daily automated backups via pg_dump
- Retention: 7 daily, 4 weekly, 3 monthly
- Backup verification via restore test weekly

## Data Models

### Post Data Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Post:
    post_id: str
    platform: str
    author: str
    content: str
    timestamp: datetime
    likes: int = 0
    comments_count: int = 0
    shares: int = 0
    url: Optional[str] = None
    author_id: Optional[str] = None
    media_type: Optional[str] = None
    hashtags: List[str] = None
    raw_data: Optional[dict] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'post_id': self.post_id,
            'platform': self.platform,
            'author': self.author,
            'author_id': self.author_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'likes': self.likes,
            'comments_count': self.comments_count,
            'shares': self.shares,
            'url': self.url,
            'media_type': self.media_type,
            'hashtags': self.hashtags or [],
            'raw_data': self.raw_data
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Post':
        """Create Post from dictionary"""
        return cls(
            post_id=data['post_id'],
            platform=data['platform'],
            author=data['author'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            likes=data.get('likes', 0),
            comments_count=data.get('comments_count', 0),
            shares=data.get('shares', 0),
            url=data.get('url'),
            author_id=data.get('author_id'),
            media_type=data.get('media_type'),
            hashtags=data.get('hashtags', []),
            raw_data=data.get('raw_data')
        )
```

### Sentiment Data Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Sentiment:
    score: float
    label: str  # 'positive', 'neutral', 'negative'
    confidence: float
    compound: float
    positive: float
    neutral: float
    negative: float
    model: str = "vader"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'score': self.score,
            'label': self.label,
            'confidence': self.confidence,
            'compound': self.compound,
            'positive': self.positive,
            'neutral': self.neutral,
            'negative': self.negative,
            'model': self.model
        }
    
    @classmethod
    def from_vader_scores(cls, scores: dict) -> 'Sentiment':
        """Create Sentiment from VADER scores"""
        compound = scores['compound']
        
        # Classify based on compound score
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Confidence is the absolute value of compound
        confidence = abs(compound)
        
        return cls(
            score=compound,
            label=label,
            confidence=confidence,
            compound=compound,
            positive=scores['pos'],
            neutral=scores['neu'],
            negative=scores['neg'],
            model='vader'
        )
```

### Execution Log Data Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ExecutionLog:
    workflow_id: str
    workflow_name: str
    status: str  # 'success', 'failed', 'partial'
    duration_ms: int
    error_message: Optional[str] = None
    error_stack: Optional[str] = None
    metadata: Optional[dict] = None
    executed_at: datetime = None
    
    def __post_init__(self):
        if self.executed_at is None:
            self.executed_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        return {
            'workflow_id': self.workflow_id,
            'workflow_name': self.workflow_name,
            'status': self.status,
            'duration_ms': self.duration_ms,
            'error_message': self.error_message,
            'error_stack': self.error_stack,
            'metadata': self.metadata,
            'executed_at': self.executed_at.isoformat()
        }
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Scraped Data Completeness

*For any* post scraped by the Scraper, the output data should contain all required fields: post_id, platform, author, content, timestamp, likes, comments_count, and shares with correct data types.

**Validates: Requirements 1.2**

### Property 2: Rate Limiting Enforcement

*For any* sequence of scraping requests, the time interval between consecutive requests should be greater than or equal to the configured rate limit delay.

**Validates: Requirements 1.3, 10.2**

### Property 3: Anti-Detection Randomization

*For any* two consecutive scraping sessions, the user agent strings and viewport dimensions should differ, demonstrating randomization.

**Validates: Requirements 1.4**

### Property 4: Scraper Output Schema Validity

*For any* scraper execution that completes successfully, the output JSON should be parseable and conform to the defined schema with metadata and posts array.

**Validates: Requirements 1.5**

### Property 5: Scraper Timeout Enforcement

*For any* scraping operation, the execution time should not exceed the configured maximum timeout value.

**Validates: Requirements 1.8**

### Property 6: Text Cleaning Removes URLs

*For any* text containing URLs, the cleaned output from TextCleaner should not contain any URL patterns (http://, https://, www.).

**Validates: Requirements 2.2**

### Property 7: Sentiment Score Validity

*For any* text analyzed by the Sentiment_Analyzer, the output should contain sentiment scores where compound, positive, neutral, and negative values are all between -1.0 and 1.0.

**Validates: Requirements 2.3**

### Property 8: Sentiment Classification Consistency

*For any* sentiment score, the label should match the classification rules: compound >= 0.05 is "positive", compound <= -0.05 is "negative", otherwise "neutral".

**Validates: Requirements 2.4**

### Property 9: Data Enrichment Preserves Original Fields

*For any* post data processed by the Sentiment_Analyzer, the output should contain all original fields from the input plus the additional sentiment fields, with original field values unchanged.

**Validates: Requirements 2.5**

### Property 10: Batch Processing Completeness

*For any* dataset with N items processed in batches of size B, the total number of processed items should equal N (no items lost during batching).

**Validates: Requirements 2.6**

### Property 11: Partial Failure Resilience

*For any* batch of items where some items fail sentiment analysis, the successfully analyzed items should still be included in the output with their sentiment data.

**Validates: Requirements 2.7**

### Property 12: Database Round-Trip Consistency

*For any* valid Post, Sentiment, or ExecutionLog object, inserting it into the database and then querying it back should return an equivalent object with all field values preserved.

**Validates: Requirements 6.2, 6.3, 6.4**

### Property 13: Duplicate Post Upsert Behavior

*For any* post with a post_id that already exists in the database, inserting it again should update the existing record rather than creating a duplicate, resulting in exactly one record with that post_id.

**Validates: Requirements 6.5**

### Property 14: Configuration Loading Correctness

*For any* set of valid environment variables, the Scraper and Sentiment_Analyzer should correctly parse and use those configuration values in their operations.

**Validates: Requirements 8.1, 8.2**

### Property 15: Missing Configuration Error Messages

*For any* required environment variable that is missing, the system should fail to start and produce an error message that specifically identifies which variable is missing.

**Validates: Requirements 8.4**

### Property 16: Credential Sanitization in Logs

*For any* log output produced by the system, it should not contain credential values, API keys, or passwords in plain text.

**Validates: Requirements 8.5**

### Property 17: Log Entry Format Completeness

*For any* log entry written by the system, it should contain a timestamp, log level (INFO, WARNING, ERROR), component identifier, and message text.

**Validates: Requirements 9.1, 9.7**

### Property 18: Error Logging with Stack Traces

*For any* exception caught by the system, the error log should contain the error message, exception type, and stack trace information.

**Validates: Requirements 9.2**

### Property 19: Log File Rotation

*For any* log file that exceeds the configured size limit, the logging system should rotate the file by renaming it with a timestamp and creating a new log file.

**Validates: Requirements 9.3**

### Property 20: Health Check Response Validity

*For any* health check request, the response should contain the service status (healthy/unhealthy) and timestamp.

**Validates: Requirements 9.5**

### Property 21: User Agent Configuration

*For any* HTTP request made by the Scraper, the request should include a User-Agent header with a valid browser user agent string.

**Validates: Requirements 10.3**

### Property 22: Retry Logic with Maximum Attempts

*For any* network request that fails, the Scraper should retry the request up to the configured maximum retry attempts before giving up.

**Validates: Requirements 11.1**

### Property 23: Exception Handling Graceful Failure

*For any* unexpected exception during scraping or analysis, the system should catch the exception, log the error details, and exit gracefully without crashing.

**Validates: Requirements 11.5**

### Property 24: Partial Data Persistence

*For any* scraping session that encounters errors after successfully scraping some posts, the successfully scraped posts should be saved to the output file before the scraper exits.

**Validates: Requirements 11.6**

### Property 25: Backup File Creation with Timestamp

*For any* backup operation, a backup file should be created with a filename that includes a timestamp in ISO format (YYYY-MM-DD-HH-MM-SS).

**Validates: Requirements 12.1**

### Property 26: Backup Storage Location

*For any* backup file created, it should be stored in the designated backup directory specified in the configuration.

**Validates: Requirements 12.2**

### Property 27: Backup Integrity Verification

*For any* backup file created, the backup script should verify the file is readable and contains valid data before marking the backup as successful.

**Validates: Requirements 12.3**

### Property 28: Backup Retention Policy Enforcement

*For any* backup directory containing backups older than the retention period, the cleanup script should delete old backups while preserving recent ones according to the retention policy (7 daily, 4 weekly, 3 monthly).

**Validates: Requirements 12.4**

## Error Handling

### Scraper Error Handling

**Authentication Errors**:
- Catch Selenium authentication exceptions
- Log error with platform and username (not password)
- Exit with error code 1
- Return empty result set

**Network Errors**:
- Implement exponential backoff retry (1s, 2s, 4s, 8s)
- Maximum 5 retry attempts
- Log each retry attempt
- If all retries fail, log final error and continue to next item

**Element Not Found Errors**:
- Log warning when expected element is missing
- Skip that specific data field
- Continue with other fields
- Mark post as "partial data" in metadata

**Timeout Errors**:
- Set page load timeout to 30 seconds
- Set script timeout to 30 seconds
- If timeout occurs, log error and skip to next post
- Implement global execution timeout (configurable, default 5 minutes)

**Rate Limit Detection**:
- Detect HTTP 429 responses or rate limit messages
- Implement exponential backoff (start with 60 seconds)
- Log rate limit detection
- Respect platform rate limits

### Sentiment Analyzer Error Handling

**Input Validation Errors**:
- Validate JSON/CSV structure before processing
- Return descriptive error if schema is invalid
- Exit with error code 2

**Text Processing Errors**:
- Catch exceptions during text cleaning
- Log error with problematic text (truncated)
- Skip that item and continue with next
- Include error count in summary

**Model Errors**:
- Catch VADER/TextBlob exceptions
- Log error with context
- Assign neutral sentiment as fallback
- Mark sentiment as "error" in metadata

**File I/O Errors**:
- Catch file read/write exceptions
- Log error with file path
- Exit with error code 3

### n8n Workflow Error Handling

**Scraper Execution Failure**:
- Check exit code from Execute Command node
- If non-zero, trigger error branch
- Send alert notification with error details
- Log to execution_logs with status "failed"
- Do not proceed to sentiment analysis

**Database Connection Failure**:
- Implement retry logic (3 attempts with 5-second delay)
- If all retries fail, save data to file for manual recovery
- Send alert to administrators
- Log error to file system

**Notification Failure**:
- Log notification failure
- Do not fail entire workflow
- Store notification in queue for retry

**Webhook Validation Failure**:
- Return HTTP 400 with JSON error response
- Include specific validation errors in response
- Log validation failure

### Database Error Handling

**Connection Errors**:
- Implement connection pooling with retry
- Maximum 3 connection attempts
- Log connection errors
- Raise exception if all attempts fail

**Constraint Violations**:
- Catch unique constraint violations (duplicate post_id)
- Perform UPDATE instead of INSERT
- Log upsert operation

**Query Errors**:
- Catch SQL exceptions
- Log query and parameters (sanitized)
- Rollback transaction
- Raise exception to caller

## Testing Strategy

### Unit Testing

**Scraper Unit Tests**:
- Test configuration loading from environment variables
- Test rate limiter token bucket algorithm
- Test anti-detection randomization (user agents, viewports)
- Test data extraction from mock HTML elements
- Test output JSON schema validation
- Test timeout enforcement
- Test retry logic with mock network failures
- Test credential sanitization in logs

**Sentiment Analyzer Unit Tests**:
- Test text cleaning functions (URL removal, whitespace normalization)
- Test sentiment classification thresholds
- Test batch processing logic
- Test error handling for invalid input
- Test data enrichment (original fields preserved)
- Test output schema validation

**Database Unit Tests**:
- Test schema creation from migration scripts
- Test CRUD operations for each table
- Test upsert logic for duplicate posts
- Test foreign key constraints
- Test index creation
- Test data retention cleanup queries

**Utility Unit Tests**:
- Test logging configuration and rotation
- Test configuration validation
- Test backup file naming with timestamps
- Test health check response format

### Property-Based Testing

All property-based tests should run with minimum 100 iterations to ensure comprehensive coverage through randomization.

**Property Test 1: Scraped Data Completeness**
- Generate random mock post elements
- Scrape data from mock elements
- Assert all required fields are present and correctly typed
- **Tag: Feature: social-media-scraper-automation, Property 1: Scraped Data Completeness**

**Property Test 2: Rate Limiting Enforcement**
- Generate random sequence of N requests (N between 10-50)
- Execute requests with rate limiter
- Measure time intervals between requests
- Assert all intervals >= configured delay
- **Tag: Feature: social-media-scraper-automation, Property 2: Rate Limiting Enforcement**

**Property Test 3: Anti-Detection Randomization**
- Execute scraper initialization twice
- Compare user agents and viewports
- Assert they are different
- Repeat 100 times to verify randomization
- **Tag: Feature: social-media-scraper-automation, Property 3: Anti-Detection Randomization**

**Property Test 4: Scraper Output Schema Validity**
- Generate random scraper outputs with varying post counts
- Parse JSON output
- Validate against schema (metadata + posts array)
- Assert schema compliance
- **Tag: Feature: social-media-scraper-automation, Property 4: Scraper Output Schema Validity**

**Property Test 5: Scraper Timeout Enforcement**
- Set random timeout values (1-10 seconds)
- Execute scraper with mock that exceeds timeout
- Assert execution terminates within timeout + grace period
- **Tag: Feature: social-media-scraper-automation, Property 5: Scraper Timeout Enforcement**

**Property Test 6: Text Cleaning Removes URLs**
- Generate random texts with embedded URLs (http, https, www)
- Clean text using TextCleaner
- Assert cleaned text contains no URL patterns
- **Tag: Feature: social-media-scraper-automation, Property 6: Text Cleaning Removes URLs**

**Property Test 7: Sentiment Score Validity**
- Generate random texts (positive, negative, neutral, mixed)
- Analyze sentiment
- Assert all scores (compound, pos, neu, neg) are in [-1.0, 1.0]
- **Tag: Feature: social-media-scraper-automation, Property 7: Sentiment Score Validity**

**Property Test 8: Sentiment Classification Consistency**
- Generate random sentiment scores across full range [-1.0, 1.0]
- Classify each score
- Assert label matches rules (>=0.05 positive, <=-0.05 negative, else neutral)
- **Tag: Feature: social-media-scraper-automation, Property 8: Sentiment Classification Consistency**

**Property Test 9: Data Enrichment Preserves Original Fields**
- Generate random post data with varying fields
- Process through sentiment analyzer
- Assert all original fields present with unchanged values
- Assert sentiment fields added
- **Tag: Feature: social-media-scraper-automation, Property 9: Data Enrichment Preserves Original Fields**

**Property Test 10: Batch Processing Completeness**
- Generate random dataset with N items (N between 50-500)
- Process in random batch sizes (10-100)
- Assert output contains exactly N items
- **Tag: Feature: social-media-scraper-automation, Property 10: Batch Processing Completeness**

**Property Test 11: Partial Failure Resilience**
- Generate random batch with some items that will fail analysis
- Process batch
- Assert successful items are in output with sentiment data
- Assert failed items are logged but don't block others
- **Tag: Feature: social-media-scraper-automation, Property 11: Partial Failure Resilience**

**Property Test 12: Database Round-Trip Consistency**
- Generate random Post, Sentiment, and ExecutionLog objects
- Insert into database
- Query back from database
- Assert retrieved objects equal original objects
- **Tag: Feature: social-media-scraper-automation, Property 12: Database Round-Trip Consistency**

**Property Test 13: Duplicate Post Upsert Behavior**
- Generate random post with unique post_id
- Insert into database
- Modify post data and insert again with same post_id
- Query database
- Assert exactly one record exists with that post_id
- Assert record has updated data
- **Tag: Feature: social-media-scraper-automation, Property 13: Duplicate Post Upsert Behavior**

**Property Test 14: Configuration Loading Correctness**
- Generate random valid environment variable sets
- Initialize scraper and analyzer with those variables
- Assert configuration values are correctly loaded and used
- **Tag: Feature: social-media-scraper-automation, Property 14: Configuration Loading Correctness**

**Property Test 15: Missing Configuration Error Messages**
- Generate random sets of environment variables with one required variable missing
- Attempt to initialize system
- Assert system fails with error message identifying the missing variable
- **Tag: Feature: social-media-scraper-automation, Property 15: Missing Configuration Error Messages**

**Property Test 16: Credential Sanitization in Logs**
- Generate random log messages that might contain credentials
- Process through logging system
- Assert log output does not contain credential values
- **Tag: Feature: social-media-scraper-automation, Property 16: Credential Sanitization in Logs**

**Property Test 17: Log Entry Format Completeness**
- Generate random log events (info, warning, error)
- Write to log
- Parse log entries
- Assert each entry contains timestamp, level, component, message
- **Tag: Feature: social-media-scraper-automation, Property 17: Log Entry Format Completeness**

**Property Test 18: Error Logging with Stack Traces**
- Generate random exceptions
- Log exceptions
- Assert log contains error message, exception type, and stack trace
- **Tag: Feature: social-media-scraper-automation, Property 18: Error Logging with Stack Traces**

**Property Test 19: Log File Rotation**
- Generate log entries until file exceeds size limit
- Assert log file is rotated (renamed with timestamp)
- Assert new log file is created
- **Tag: Feature: social-media-scraper-automation, Property 19: Log File Rotation**

**Property Test 20: Health Check Response Validity**
- Execute health check multiple times
- Assert each response contains status and timestamp
- Assert timestamp is recent (within last 5 seconds)
- **Tag: Feature: social-media-scraper-automation, Property 20: Health Check Response Validity**

**Property Test 21: User Agent Configuration**
- Generate random scraper requests
- Inspect HTTP headers
- Assert User-Agent header is present and valid
- **Tag: Feature: social-media-scraper-automation, Property 21: User Agent Configuration**

**Property Test 22: Retry Logic with Maximum Attempts**
- Generate random network failures
- Execute requests with retry logic
- Count retry attempts
- Assert retries <= configured maximum
- Assert final failure after max retries
- **Tag: Feature: social-media-scraper-automation, Property 22: Retry Logic with Maximum Attempts**

**Property Test 23: Exception Handling Graceful Failure**
- Generate random unexpected exceptions during scraping
- Execute scraper
- Assert exceptions are caught and logged
- Assert scraper exits gracefully (no crash)
- **Tag: Feature: social-media-scraper-automation, Property 23: Exception Handling Graceful Failure**

**Property Test 24: Partial Data Persistence**
- Generate scraping session that fails after N successful posts
- Execute scraper
- Assert output file contains the N successful posts
- **Tag: Feature: social-media-scraper-automation, Property 24: Partial Data Persistence**

**Property Test 25: Backup File Creation with Timestamp**
- Execute backup operation multiple times
- Assert each backup file has timestamp in filename
- Assert timestamps are in ISO format
- **Tag: Feature: social-media-scraper-automation, Property 25: Backup File Creation with Timestamp**

**Property Test 26: Backup Storage Location**
- Generate random backup operations
- Execute backups
- Assert all backup files are in designated backup directory
- **Tag: Feature: social-media-scraper-automation, Property 26: Backup Storage Location**

**Property Test 27: Backup Integrity Verification**
- Create random backups
- Run integrity verification
- Assert verification succeeds for valid backups
- Assert verification fails for corrupted backups
- **Tag: Feature: social-media-scraper-automation, Property 27: Backup Integrity Verification**

**Property Test 28: Backup Retention Policy Enforcement**
- Generate backup directory with random old and recent backups
- Run retention cleanup
- Assert old backups (beyond retention period) are deleted
- Assert recent backups are preserved
- **Tag: Feature: social-media-scraper-automation, Property 28: Backup Retention Policy Enforcement**

### Integration Testing

**End-to-End Scraping Flow**:
- Set up test social media account or use mock server
- Execute full scraping workflow
- Verify data is scraped, analyzed, stored, and reported
- Verify notifications are sent

**Database Integration**:
- Test with actual PostgreSQL instance
- Verify schema creation
- Test data persistence across container restarts
- Test backup and restore procedures

**n8n Workflow Integration**:
- Import workflow JSON into n8n instance
- Execute workflows with test data
- Verify workflow nodes execute in correct order
- Verify error handling branches work

**Docker Compose Integration**:
- Start all services with docker-compose up
- Verify inter-service connectivity
- Verify volume persistence
- Verify environment variable loading
- Test graceful shutdown and restart

### Performance Testing

**Scraping Performance**:
- Measure time to scrape 100, 500, 1000 posts
- Verify rate limiting doesn't cause excessive delays
- Monitor memory usage during large scrapes

**Sentiment Analysis Performance**:
- Measure time to analyze 1000, 5000, 10000 texts
- Test batch processing efficiency
- Monitor memory usage with large batches

**Database Performance**:
- Test query performance with 10k, 100k, 1M records
- Verify indexes improve query speed
- Test concurrent write performance

### Security Testing

**Credential Protection**:
- Verify no credentials in logs
- Verify no credentials in error messages
- Verify environment variables are not exposed

**SQL Injection Prevention**:
- Test database queries with malicious input
- Verify parameterized queries prevent injection

**Container Security**:
- Verify containers run as non-root users
- Verify no unnecessary ports exposed
- Scan images for vulnerabilities

