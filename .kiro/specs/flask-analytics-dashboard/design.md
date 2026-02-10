# Design Document: Flask Analytics Dashboard

## Overview

The Flask Analytics Dashboard is a lightweight web application that provides interactive visualizations of Instagram scraping data stored in PostgreSQL. Built with Flask, the dashboard offers five main pages (Home, Sentiment Analysis, Engagement Metrics, Content Analysis, and Data Explorer) with responsive design, RESTful API endpoints, and real-time data updates. The application reuses the existing database schema and operations from the `database/` module, ensuring compatibility with the Grafana integration while providing greater customization flexibility.

The architecture follows a three-tier pattern: a Flask backend serving both HTML pages and JSON APIs, a PostgreSQL database layer accessed through the existing Database_Module, and a JavaScript frontend using Chart.js for interactive visualizations. Query result caching with Flask-Caching ensures sub-2-second page loads, while Bootstrap provides responsive styling for mobile and desktop devices.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  HTML Pages  │  │  JavaScript  │  │   Chart.js   │ │
│  │  (Jinja2)    │  │  (AJAX)      │  │  (Visualize) │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          │ HTTP             │ AJAX/JSON        │
          ▼                  ▼                  │
┌─────────────────────────────────────────────────────────┐
│              Flask Application (app.py)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Routes     │  │  API Routes  │  │    Cache     │ │
│  │  (HTML)      │  │  (JSON)      │  │   Manager    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                            │                            │
│                            ▼                            │
│                  ┌──────────────────┐                  │
│                  │  Service Layer   │                  │
│                  │  (data queries)  │                  │
│                  └─────────┬────────┘                  │
└────────────────────────────┼─────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│              Database Module (existing)                 │
│  ┌──────────────┐  ┌──────────────┐                   │
│  │db_connection │  │db_operations │                   │
│  │    .py       │  │    .py       │                   │
│  └──────┬───────┘  └──────┬───────┘                   │
└─────────┼──────────────────┼───────────────────────────┘
          │                  │
          └────────┬─────────┘
                   ▼
          ┌─────────────────┐
          │   PostgreSQL    │
          │    Database     │
          └─────────────────┘
```

### Component Interaction Flow

1. **Page Load Flow**: Browser requests HTML page → Flask route renders Jinja2 template → Template includes JavaScript that makes AJAX calls → API endpoints return JSON → Chart.js renders visualizations
2. **Data Query Flow**: API endpoint receives request → Check cache → If miss, query database via Database_Module → Transform data for visualization → Cache result → Return JSON
3. **Data Import Flow**: Import script reads JSON/CSV files → Validates data → Calls Database_Module operations → Inserts/updates database → Invalidates cache

## Components and Interfaces

### 1. Flask Application (`app.py`)

**Responsibilities:**
- Initialize Flask app with configuration
- Register routes for HTML pages and API endpoints
- Configure Flask-Caching
- Handle error responses and logging
- Serve static files and templates

**Key Functions:**
- `create_app()`: Factory function to create and configure Flask app
- `init_cache()`: Initialize cache manager with configuration
- `init_logging()`: Configure logging to file and console
- `register_routes()`: Register all route blueprints

**Configuration:**
```python
class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'instagram_analytics')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))
    AUTO_REFRESH_INTERVAL = int(os.getenv('AUTO_REFRESH_INTERVAL', '30'))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
```

### 2. Routes Module (`routes/pages.py`)

**Responsibilities:**
- Define routes for HTML page rendering
- Pass configuration to templates
- Handle page-specific logic

**Routes:**
- `GET /` → Home/Overview page
- `GET /sentiment` → Sentiment Analysis page
- `GET /engagement` → Engagement Metrics page
- `GET /content` → Content Analysis page
- `GET /explorer` → Data Explorer page

**Interface:**
```python
@pages_bp.route('/')
def home():
    """Render home page with overview statistics"""
    return render_template('home.html', 
                         refresh_interval=current_app.config['AUTO_REFRESH_INTERVAL'])

@pages_bp.route('/sentiment')
def sentiment():
    """Render sentiment analysis page"""
    return render_template('sentiment.html')
```

### 3. API Routes Module (`routes/api.py`)

**Responsibilities:**
- Define RESTful API endpoints
- Query data via service layer
- Return JSON responses
- Handle query parameters (date ranges, filters, pagination)
- Apply caching to responses

**Endpoints:**
- `GET /api/summary` → Overall statistics
- `GET /api/sentiment?start_date=&end_date=` → Sentiment data
- `GET /api/engagement?start_date=&end_date=` → Engagement metrics
- `GET /api/content?start_date=&end_date=` → Content analysis
- `GET /api/posts?page=&per_page=&search=&filter=` → Paginated posts
- `GET /api/export?filters=` → CSV export

**Interface:**
```python
@api_bp.route('/api/summary')
@cache.cached(timeout=300)
def get_summary():
    """Return overall statistics"""
    data = service.get_summary_stats()
    return jsonify(data)

@api_bp.route('/api/sentiment')
@cache.cached(timeout=300, query_string=True)
def get_sentiment():
    """Return sentiment analysis data with optional date filtering"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = service.get_sentiment_data(start_date, end_date)
    return jsonify(data)
```

### 4. Service Layer (`services/data_service.py`)

**Responsibilities:**
- Business logic for data queries
- Data transformation for visualizations
- Aggregation and calculation of metrics
- Interface with Database_Module

**Key Functions:**
```python
def get_summary_stats() -> dict:
    """Get overall statistics for home page"""
    # Returns: {total_posts, total_comments, avg_sentiment, last_execution, post_type_distribution}

def get_sentiment_data(start_date: str = None, end_date: str = None) -> dict:
    """Get sentiment distribution and trends"""
    # Returns: {distribution: {positive, neutral, negative}, trends: [{date, score}], gauge: avg_score}

def get_engagement_data(start_date: str = None, end_date: str = None) -> dict:
    """Get engagement metrics and top posts"""
    # Returns: {top_posts: [...], trends: [...], type_distribution: {...}}

def get_content_data(start_date: str = None, end_date: str = None) -> dict:
    """Get content analysis data"""
    # Returns: {hashtags: [...], posting_heatmap: [...], length_distribution: [...]}

def get_posts_paginated(page: int, per_page: int, search: str = None, filters: dict = None) -> dict:
    """Get paginated posts with search and filters"""
    # Returns: {posts: [...], total: int, page: int, per_page: int, total_pages: int}

def export_posts_csv(filters: dict = None) -> str:
    """Generate CSV file of filtered posts"""
    # Returns: CSV file path
```

**Data Transformation Examples:**
```python
def classify_sentiment(score: float) -> str:
    """Classify sentiment score into category"""
    if score > 0.05:
        return 'positive'
    elif score < -0.05:
        return 'negative'
    else:
        return 'neutral'

def calculate_engagement_rate(likes: int, comments: int, followers: int) -> float:
    """Calculate engagement rate as percentage"""
    if followers == 0:
        return 0.0
    return ((likes + comments) / followers) * 100

def extract_hashtags(caption: str) -> list:
    """Extract hashtags from caption text"""
    import re
    return re.findall(r'#(\w+)', caption)
```

### 5. Database Module Integration

**Existing Module Usage:**
- `database/db_connection.py`: Connection management
- `database/db_operations.py`: CRUD operations

**Required New Functions in `db_operations.py`:**
```python
def get_posts_with_sentiment(start_date=None, end_date=None):
    """Get posts joined with sentiment analysis"""
    # JOIN posts with sentiment_analysis table

def get_sentiment_distribution(start_date=None, end_date=None):
    """Get count of posts by sentiment category"""
    # Aggregate sentiment scores into categories

def get_top_posts_by_engagement(limit=10, start_date=None, end_date=None):
    """Get posts sorted by engagement rate"""
    # Calculate and sort by (likes + comments) / followers

def get_hashtag_frequency(start_date=None, end_date=None):
    """Get hashtag counts from post captions"""
    # Extract and count hashtags

def get_posting_time_heatmap(start_date=None, end_date=None):
    """Get post counts by day of week and hour"""
    # Group by EXTRACT(DOW) and EXTRACT(HOUR)

def search_posts(search_term, filters=None, page=1, per_page=25):
    """Search posts with pagination"""
    # Full-text search on caption and author
```

### 6. Templates (`templates/`)

**Base Template (`base.html`):**
- Navigation menu
- Theme toggle
- Common CSS/JS includes
- Flash message display

**Page Templates:**
- `home.html`: Overview dashboard with summary cards
- `sentiment.html`: Sentiment visualizations (pie, line, gauge)
- `engagement.html`: Engagement metrics (table, time series, pie)
- `content.html`: Content analysis (hashtag chart, heatmap, histogram)
- `explorer.html`: Data table with search, filters, export

**Template Structure:**
```html
{% extends "base.html" %}
{% block content %}
<div class="container">
    <h1>Page Title</h1>
    <div class="row">
        <div class="col-md-6">
            <canvas id="chart1"></canvas>
        </div>
        <div class="col-md-6">
            <canvas id="chart2"></canvas>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/page_specific.js') }}"></script>
{% endblock %}
```

### 7. Static Assets (`static/`)

**JavaScript Files:**
- `static/js/common.js`: Shared utilities (AJAX helpers, date formatting, theme toggle)
- `static/js/home.js`: Home page chart initialization
- `static/js/sentiment.js`: Sentiment page charts
- `static/js/engagement.js`: Engagement page charts
- `static/js/content.js`: Content page charts
- `static/js/explorer.js`: Data table, search, filters, export

**CSS Files:**
- `static/css/style.css`: Custom styles, theme variables, chart styling

**JavaScript Chart Initialization Pattern:**
```javascript
// Fetch data from API
async function loadChartData() {
    const response = await fetch('/api/sentiment?start_date=' + startDate + '&end_date=' + endDate);
    const data = await response.json();
    return data;
}

// Initialize Chart.js chart
function initSentimentPieChart(data) {
    const ctx = document.getElementById('sentimentPie').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [data.distribution.positive, data.distribution.neutral, data.distribution.negative],
                backgroundColor: ['#28a745', '#ffc107', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: { enabled: true }
            }
        }
    });
}

// Load and render on page load
document.addEventListener('DOMContentLoaded', async () => {
    const data = await loadChartData();
    initSentimentPieChart(data);
});
```

### 8. Data Import Script (`scripts/import_data.py`)

**Responsibilities:**
- Read JSON/CSV files from output directories
- Validate data format
- Insert/update database records
- Handle duplicates (upsert logic)
- Provide CLI interface
- Invalidate cache after import

**CLI Interface:**
```bash
python scripts/import_data.py --input output/instagram/raw/ --type json
python scripts/import_data.py --input output/instagram/sentiment/ --type csv --batch
python scripts/import_data.py --file output/instagram/raw/posts_20260209.json
```

**Key Functions:**
```python
def read_json_file(file_path: str) -> list:
    """Read and parse JSON file"""

def read_csv_file(file_path: str) -> list:
    """Read and parse CSV file"""

def validate_post_data(post: dict) -> bool:
    """Validate required fields exist"""

def import_posts(posts: list) -> tuple:
    """Import posts with upsert logic, returns (inserted, updated)"""

def invalidate_cache():
    """Clear Flask cache after import"""
```

## Data Models

The application uses the existing database schema from `database/migrations/001_initial_schema.sql`. No modifications to the schema are required.

**Key Tables:**

1. **posts**: Instagram post data
   - Columns: id, post_id, author, caption, likes, comments, followers, post_type, timestamp, etc.

2. **comments**: Post comments
   - Columns: id, post_id, comment_id, author, text, timestamp, etc.

3. **sentiment_analysis**: Sentiment scores for posts
   - Columns: id, post_id, sentiment_score, sentiment_label, analysis_timestamp, etc.

4. **scraping_executions**: Execution metadata
   - Columns: id, execution_id, start_time, end_time, status, posts_scraped, etc.

**Data Transfer Objects (DTOs):**

```python
@dataclass
class SummaryStats:
    total_posts: int
    total_comments: int
    avg_sentiment: float
    last_execution: datetime
    post_type_distribution: dict

@dataclass
class SentimentData:
    distribution: dict  # {positive: int, neutral: int, negative: int}
    trends: list  # [{date: str, score: float}]
    gauge: float  # Average sentiment score

@dataclass
class EngagementData:
    top_posts: list  # [{post_id, author, caption, engagement_rate, likes, comments}]
    trends: list  # [{date: str, engagement_rate: float}]
    type_distribution: dict  # {posts: int, reels: int}

@dataclass
class ContentData:
    hashtags: list  # [{tag: str, count: int}]
    posting_heatmap: list  # [{day: int, hour: int, count: int}]
    length_distribution: list  # [{bin: str, count: int}]

@dataclass
class PostsPage:
    posts: list
    total: int
    page: int
    per_page: int
    total_pages: int
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several areas where properties can be consolidated:

**Date Range Filtering**: Requirements 4.4, 6.4, and 8.6 all test date range filtering across different pages/endpoints. These can be combined into a single comprehensive property that validates filtering works correctly across all API endpoints.

**Error Handling**: Requirements 1.5, 8.8, 14.2, and 14.5 all test error handling behavior. These can be consolidated into properties that validate error responses are consistent across all error types.

**Configuration Defaults**: Requirements 13.2, 13.3, 13.4, and 13.6 all test default configuration values. These can be combined into a single property about default value handling.

**Logging**: Requirements 14.3 and 14.5 both test logging behavior and can be combined into a comprehensive logging property.

The following properties represent the unique, non-redundant validation requirements:

### Property 1: Sentiment Classification Consistency

*For any* sentiment score value, the classification function should return "positive" when score > 0.05, "neutral" when -0.05 ≤ score ≤ 0.05, and "negative" when score < -0.05.

**Validates: Requirements 4.5**

### Property 2: Engagement Rate Calculation

*For any* post with likes, comments, and followers values, the engagement rate should equal ((likes + comments) / followers) * 100, or 0.0 when followers is 0.

**Validates: Requirements 5.5**

### Property 3: Date Range Filtering Consistency

*For any* API endpoint that accepts date range parameters (start_date, end_date) and any valid date range, all returned results should have timestamps within the specified range (inclusive).

**Validates: Requirements 4.4, 6.4, 8.6**

### Property 4: Hashtag Extraction Completeness

*For any* post caption text, the hashtag extraction function should return all substrings that match the pattern #(\w+), preserving the order they appear in the caption.

**Validates: Requirements 6.5**

### Property 5: Search Term Filtering

*For any* search term and any set of posts, the filtered results should only include posts where either the caption or author field contains the search term (case-insensitive).

**Validates: Requirements 7.2**

### Property 6: Filter Combination Correctness

*For any* combination of filters (date range, post type, sentiment category, search term), the filtered results should satisfy all filter conditions simultaneously (logical AND).

**Validates: Requirements 7.3**

### Property 7: Column Sorting Correctness

*For any* column name and sort direction (ascending/descending), the sorted results should be ordered according to the column values in the specified direction.

**Validates: Requirements 7.7**

### Property 8: Invalid Parameter Error Handling

*For any* API endpoint and any invalid parameter value (malformed dates, negative page numbers, invalid filter values), the endpoint should return a 400 status code with a JSON error message describing the validation failure.

**Validates: Requirements 8.8**

### Property 9: Duplicate Post Upsert Behavior

*For any* post with a unique post_id, importing the same post multiple times should result in exactly one database record with the most recent data, not multiple duplicate records.

**Validates: Requirements 9.3**

### Property 10: Invalid Record Validation

*For any* data record missing required fields (post_id, author, timestamp), the import script should skip the record, log a warning message, and continue processing remaining records.

**Validates: Requirements 9.7**

### Property 11: Configuration Default Fallback

*For any* configuration parameter with a defined default value, when the corresponding environment variable is not set, the application should use the default value and log a warning.

**Validates: Requirements 13.6**

### Property 12: API Error Response Format

*For any* error that occurs during API endpoint processing, the response should be valid JSON containing an "error" field with a descriptive message and return an appropriate HTTP status code (4xx for client errors, 5xx for server errors).

**Validates: Requirements 14.2**

### Property 13: Unhandled Exception Logging

*For any* unhandled exception that occurs during request processing, the application should log the full stack trace including exception type, message, and traceback, then return a 500 status code.

**Validates: Requirements 14.5**

### Property 14: HTTP Request Logging Completeness

*For any* HTTP request received by the Flask application, the log should contain an entry with timestamp, HTTP method, request path, and response status code.

**Validates: Requirements 14.3**

## Error Handling

### Error Categories

1. **Database Connection Errors**
   - Scenario: PostgreSQL is unavailable or credentials are invalid
   - Handling: Log error with full details, display user-friendly error page, return 503 Service Unavailable
   - Recovery: Implement connection retry logic with exponential backoff

2. **Query Execution Errors**
   - Scenario: SQL query fails due to syntax error or constraint violation
   - Handling: Log error with query details, return 500 Internal Server Error with generic message
   - Recovery: Rollback transaction, return empty result set or error response

3. **Data Validation Errors**
   - Scenario: API receives invalid parameters (malformed dates, negative numbers)
   - Handling: Return 400 Bad Request with specific validation error message
   - Recovery: Client should correct parameters and retry

4. **File I/O Errors (Import Script)**
   - Scenario: JSON/CSV file is missing, corrupted, or has invalid format
   - Handling: Log error with file path, skip file, continue with remaining files
   - Recovery: User should verify file format and retry import

5. **Cache Errors**
   - Scenario: Cache backend (Redis) is unavailable
   - Handling: Log warning, fall back to direct database queries
   - Recovery: Continue operation without caching, attempt cache reconnection

6. **Template Rendering Errors**
   - Scenario: Jinja2 template has syntax error or missing variable
   - Handling: Log error with template name and line number, return 500 error page
   - Recovery: Fix template syntax, restart application

### Error Response Format

**API Endpoints (JSON):**
```json
{
    "error": "Invalid date format for start_date parameter",
    "status": 400,
    "timestamp": "2024-02-09T15:30:00Z"
}
```

**HTML Pages:**
- Display user-friendly error page with error code and message
- Provide link to return to home page
- Log detailed error information for debugging

### Logging Strategy

**Log Levels:**
- DEBUG: Database queries, cache hits/misses, detailed request info
- INFO: HTTP requests, successful operations, startup/shutdown
- WARNING: Missing configuration, cache failures, skipped records
- ERROR: Database errors, API errors, failed operations
- CRITICAL: Application startup failures, unrecoverable errors

**Log Format:**
```
[2024-02-09 15:30:00,123] [INFO] [app.routes.api] GET /api/sentiment?start_date=2024-01-01 - 200 OK (45ms)
[2024-02-09 15:30:05,456] [ERROR] [app.services.data_service] Database query failed: connection timeout
```

**Log Rotation:**
- Maximum file size: 10 MB
- Keep last 5 log files
- Log file location: `logs/flask_dashboard.log`

## Testing Strategy

### Dual Testing Approach

The testing strategy employs both unit tests and property-based tests to ensure comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and integration points
- **Property tests**: Verify universal properties across all inputs using randomized testing

Both approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across a wide range of inputs.

### Property-Based Testing

**Library Selection:**
- Python: Use `hypothesis` library for property-based testing
- Minimum 100 iterations per property test (configurable via `@settings(max_examples=100)`)

**Test Tagging:**
Each property test must include a comment referencing the design document property:
```python
@given(sentiment_score=floats(min_value=-1.0, max_value=1.0))
@settings(max_examples=100)
def test_sentiment_classification_consistency(sentiment_score):
    """
    Feature: flask-analytics-dashboard, Property 1: Sentiment Classification Consistency
    For any sentiment score value, the classification function should return
    "positive" when score > 0.05, "neutral" when -0.05 ≤ score ≤ 0.05,
    and "negative" when score < -0.05.
    """
    result = classify_sentiment(sentiment_score)
    
    if sentiment_score > 0.05:
        assert result == "positive"
    elif sentiment_score < -0.05:
        assert result == "negative"
    else:
        assert result == "neutral"
```

**Property Test Coverage:**
- Property 1: Sentiment classification (100+ random scores)
- Property 2: Engagement rate calculation (100+ random post data)
- Property 3: Date range filtering (100+ random date ranges)
- Property 4: Hashtag extraction (100+ random captions)
- Property 5: Search filtering (100+ random search terms)
- Property 6: Filter combinations (100+ random filter sets)
- Property 7: Column sorting (100+ random sort requests)
- Property 8: Invalid parameter handling (100+ random invalid inputs)
- Property 9: Duplicate post upsert (100+ random duplicate scenarios)
- Property 10: Invalid record validation (100+ random invalid records)
- Property 11: Configuration defaults (100+ random missing config scenarios)
- Property 12: API error responses (100+ random error conditions)
- Property 13: Exception logging (100+ random exceptions)
- Property 14: Request logging (100+ random requests)

### Unit Testing

**Test Organization:**
```
tests/
├── unit/
│   ├── test_routes_pages.py      # HTML page routes
│   ├── test_routes_api.py        # API endpoint routes
│   ├── test_services.py          # Data service layer
│   ├── test_import_script.py     # Import script functions
│   └── test_utils.py             # Utility functions
├── integration/
│   ├── test_api_integration.py   # End-to-end API tests
│   ├── test_database.py          # Database operations
│   └── test_caching.py           # Cache behavior
└── property/
    ├── test_properties_core.py   # Properties 1-7
    ├── test_properties_errors.py # Properties 8, 12-14
    └── test_properties_import.py # Properties 9-11
```

**Unit Test Focus Areas:**
1. **Route Tests**: Verify routes return correct status codes and templates
2. **API Tests**: Verify endpoints return correct JSON structure
3. **Service Tests**: Verify data transformations and calculations
4. **Import Tests**: Verify file reading and database insertion
5. **Cache Tests**: Verify cache hit/miss behavior
6. **Error Tests**: Verify specific error scenarios (connection failure, invalid file)
7. **Configuration Tests**: Verify environment variable loading

**Example Unit Test:**
```python
def test_summary_endpoint_returns_correct_structure():
    """Test that /api/summary returns expected JSON structure"""
    response = client.get('/api/summary')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'total_posts' in data
    assert 'total_comments' in data
    assert 'avg_sentiment' in data
    assert 'last_execution' in data
    assert 'post_type_distribution' in data
    
    assert isinstance(data['total_posts'], int)
    assert isinstance(data['avg_sentiment'], float)
```

**Edge Cases to Test:**
- Empty database (no posts)
- Single post in database
- Posts with zero followers (engagement rate calculation)
- Captions with no hashtags
- Captions with only hashtags
- Date ranges with no matching posts
- Malformed date strings
- Negative page numbers
- Page numbers beyond available data
- Missing required fields in import data
- Duplicate post_ids with different data

### Integration Testing

**Database Integration:**
- Use test database with known data
- Test queries return expected results
- Test transactions and rollbacks
- Test connection pooling

**Cache Integration:**
- Test cache hit/miss scenarios
- Test cache expiration
- Test cache invalidation on import
- Test fallback when cache unavailable

**End-to-End API Tests:**
- Test complete request/response cycle
- Test authentication (if added later)
- Test CORS headers
- Test error responses

### Test Execution

**Running Tests:**
```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only property tests
pytest tests/property/

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific property test with verbose output
pytest tests/property/test_properties_core.py::test_sentiment_classification_consistency -v
```

**Continuous Integration:**
- Run all tests on every commit
- Require 80%+ code coverage
- Fail build on any test failure
- Generate coverage reports

### Manual Testing Checklist

While automated tests cover most functionality, manual testing should verify:
- [ ] Responsive design on mobile devices
- [ ] Theme switching (light/dark mode)
- [ ] Chart interactivity (hover, click, zoom)
- [ ] Auto-refresh functionality
- [ ] CSV export downloads correctly
- [ ] Navigation menu behavior
- [ ] Loading indicators display correctly
- [ ] Error pages display user-friendly messages
