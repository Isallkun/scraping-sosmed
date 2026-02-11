# Database Integration Documentation

## Overview

The Flask Analytics Dashboard integrates with the existing PostgreSQL database module located in `database/`. This integration provides connection pooling, automatic retry logic, and Flask application lifecycle management.

## Architecture

```
Flask App (app/)
    ↓
app/database.py (wrapper)
    ↓
database/db_connection.py (connection pooling)
    ↓
database/db_operations.py (CRUD operations)
    ↓
PostgreSQL Database
```

## Components

### 1. `app/database.py`

Wrapper module that integrates the database with Flask:

- **`init_database(app)`**: Initializes database connection pool on app startup
- **`get_db()`**: Returns database connection for current request context
- **`test_database_connection(app)`**: Tests database connectivity
- **`get_database_info()`**: Returns database connection information

### 2. `database/db_connection.py`

Manages database connections with pooling:

- **`DatabaseConnection`**: Connection pool manager class
- **`get_db_connection()`**: Returns global database instance (singleton)
- **`close_db_connection()`**: Closes all connections

### 3. `database/db_operations.py`

Provides CRUD operations:

- `insert_post()`: Insert/update posts with upsert logic
- `insert_sentiment()`: Insert sentiment analysis results
- `insert_execution_log()`: Log workflow executions
- `get_posts_with_sentiment()`: Query posts with sentiment data
- `get_sentiment_distribution()`: Get sentiment statistics
- `get_top_posts_by_engagement()`: Get most engaging posts
- And more...

## Configuration

Database configuration is read from environment variables:

```bash
# Database connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social_scraper
DB_USER=postgres
DB_PASSWORD=your_password

# Connection pooling
DB_POOL_MIN_CONN=2
DB_POOL_MAX_CONN=10
DB_CONNECT_TIMEOUT=10
```

## Usage in Flask Routes

### Example 1: Using database operations

```python
from app.database import get_db
from database import db_operations
from datetime import datetime, timedelta

@app.route('/api/posts')
def get_posts():
    """Get posts from last 7 days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    posts = db_operations.get_posts_by_date_range(
        start_date=start_date,
        end_date=end_date,
        platform='instagram'
    )
    
    return jsonify(posts)
```

### Example 2: Using raw queries

```python
from app.database import get_db

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    db = get_db()
    
    with db.get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM posts")
        post_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sentiments")
        sentiment_count = cursor.fetchone()[0]
    
    return jsonify({
        'posts': post_count,
        'sentiments': sentiment_count
    })
```

### Example 3: Using transactions

```python
from app.database import get_db

@app.route('/api/import', methods=['POST'])
def import_data():
    """Import data with transaction"""
    db = get_db()
    
    try:
        with db.get_cursor(commit=True) as cursor:
            # Multiple operations in a transaction
            cursor.execute("INSERT INTO posts ...")
            cursor.execute("INSERT INTO sentiments ...")
            # Automatically commits on success
        
        return jsonify({'status': 'success'})
    except Exception as e:
        # Automatically rolls back on error
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

## Connection Pooling

The database module uses connection pooling to optimize performance:

- **Minimum connections**: 2 (configurable via `DB_POOL_MIN_CONN`)
- **Maximum connections**: 10 (configurable via `DB_POOL_MAX_CONN`)
- **Connection timeout**: 10 seconds (configurable via `DB_CONNECT_TIMEOUT`)

Benefits:
- Reduces connection overhead
- Handles concurrent requests efficiently
- Automatic connection reuse
- Graceful connection cleanup

## Error Handling

The integration includes comprehensive error handling:

1. **Connection failures**: Automatic retry with exponential backoff (3 attempts)
2. **Query failures**: Automatic transaction rollback
3. **Pool exhaustion**: Graceful error messages
4. **Startup failures**: App continues but logs errors

Example error handling:

```python
from database.db_connection import DatabaseConnectionError
from database.db_operations import DatabaseOperationError

try:
    posts = db_operations.get_posts_by_date_range(start_date, end_date)
except DatabaseConnectionError as e:
    # Connection-level error
    logger.error(f"Database connection failed: {e}")
    return jsonify({'error': 'Database unavailable'}), 503
except DatabaseOperationError as e:
    # Query-level error
    logger.error(f"Query failed: {e}")
    return jsonify({'error': 'Query failed'}), 500
```

## Testing

### Running the integration test

```bash
python test_db_integration.py
```

This test verifies:
- Flask app creation
- Database connection initialization
- Connection pooling configuration
- Query execution
- Database schema existence

### Manual testing

```python
from app import create_app
from app.database import get_db, get_database_info

app = create_app()

with app.app_context():
    # Get database info
    info = get_database_info()
    print(info)
    
    # Test connection
    db = get_db()
    print(db.test_connection())
```

## Database Schema

The database uses the schema defined in `database/migrations/001_initial_schema.sql`:

### Tables

1. **posts**: Social media posts
   - Columns: id, post_id, platform, author, content, timestamp, likes, comments_count, etc.
   - Indexes: platform, timestamp, author, scraped_at

2. **sentiments**: Sentiment analysis results
   - Columns: id, post_id (FK), score, label, confidence, compound, etc.
   - Indexes: post_id, label, processed_at

3. **execution_logs**: Workflow execution logs
   - Columns: id, workflow_id, workflow_name, status, duration_ms, etc.
   - Indexes: workflow_id, status, executed_at

### Relationships

- `sentiments.post_id` → `posts.id` (CASCADE DELETE)

## Initialization

### First-time setup

1. Create the database:
```bash
psql -U postgres -c "CREATE DATABASE social_scraper;"
```

2. Run the schema migration:
```bash
psql -U postgres -d social_scraper -f database/migrations/001_initial_schema.sql
```

3. Set environment variables in `.env`:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social_scraper
DB_USER=postgres
DB_PASSWORD=your_password
```

4. Test the connection:
```bash
python test_db_integration.py
```

## Troubleshooting

### Connection refused

**Problem**: `connection refused` error

**Solution**: 
- Ensure PostgreSQL is running: `pg_ctl status`
- Check connection parameters in `.env`
- Verify firewall settings

### Database does not exist

**Problem**: `database "social_scraper" does not exist`

**Solution**:
```bash
psql -U postgres -c "CREATE DATABASE social_scraper;"
psql -U postgres -d social_scraper -f database/migrations/001_initial_schema.sql
```

### Authentication failed

**Problem**: `authentication failed for user`

**Solution**:
- Verify `DB_USER` and `DB_PASSWORD` in `.env`
- Check PostgreSQL `pg_hba.conf` authentication settings

### Pool exhausted

**Problem**: `No connections available in pool`

**Solution**:
- Increase `DB_POOL_MAX_CONN` in `.env`
- Check for connection leaks (ensure connections are returned)
- Review concurrent request load

## Performance Considerations

1. **Connection pooling**: Reuses connections to minimize overhead
2. **Indexes**: Database has indexes on frequently queried columns
3. **Prepared statements**: All queries use parameterized statements
4. **Transaction management**: Automatic commit/rollback handling
5. **Connection timeout**: Prevents hanging connections

## Security

1. **Parameterized queries**: All queries use parameters to prevent SQL injection
2. **Connection string**: Sensitive credentials read from environment variables
3. **Error messages**: Don't expose sensitive connection details in logs
4. **Connection cleanup**: Automatic cleanup on app shutdown

## Requirements Validation

This integration validates the following requirements:

- **Requirement 1.2**: Flask app connects to PostgreSQL database using Database_Module
- **Requirement 12.6**: Database module uses connection pooling to minimize connection overhead
- **Requirement 15.5**: Flask app uses Database_Module functions from `database/db_operations.py`

## Next Steps

After database integration, the next tasks are:

1. Implement service layer for data queries (`app/services/data_service.py`)
2. Add new database query functions to `database/db_operations.py`
3. Implement API routes (`app/routes/api.py`)
4. Implement caching layer with Flask-Caching
