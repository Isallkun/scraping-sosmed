# Database Module

This module provides database connectivity and operations for the Social Media Scraper Automation system.

## Features

- **Connection Pooling**: Efficient connection management using psycopg2 connection pool
- **Automatic Retry Logic**: Configurable retry mechanism for handling connection failures
- **Environment Configuration**: Load database settings from environment variables
- **Context Managers**: Clean and safe database operations with automatic cleanup
- **Singleton Pattern**: Global database instance for application-wide use
- **Error Handling**: Comprehensive error handling with descriptive messages

## Installation

The database module requires psycopg2-binary:

```bash
pip install psycopg2-binary
```

## Configuration

Configure database connection using environment variables in your `.env` file:

### Option 1: Using DATABASE_URL (Recommended)

```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### Option 2: Using Individual Parameters

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social_scraper
DB_USER=scraper_user
DB_PASSWORD=your_password
```

### Optional Configuration

```env
# Connection pool settings
DB_POOL_MIN_CONN=2          # Minimum connections in pool (default: 2)
DB_POOL_MAX_CONN=10         # Maximum connections in pool (default: 10)

# Connection timeout
DB_CONNECT_TIMEOUT=10       # Timeout in seconds (default: 10)
```

## Usage

### Basic Usage

```python
from database.db_connection import DatabaseConnection

# Create database connection
db = DatabaseConnection()

# Test connection
if db.test_connection():
    print("Connected successfully!")

# Execute query
with db.get_cursor() as cursor:
    cursor.execute("SELECT * FROM posts LIMIT 10")
    results = cursor.fetchall()
    for row in results:
        print(row)

# Close connections when done
db.close_all_connections()
```

### Using Context Manager (Recommended)

```python
from database.db_connection import DatabaseConnection

# Automatic cleanup with context manager
with DatabaseConnection() as db:
    with db.get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM posts")
        count = cursor.fetchone()[0]
        print(f"Total posts: {count}")
# Connections automatically closed
```

### Transactions with Commit

```python
from database.db_connection import DatabaseConnection

with DatabaseConnection() as db:
    # Insert data with automatic commit
    with db.get_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO posts (post_id, platform, content) VALUES (%s, %s, %s)",
            ("abc123", "instagram", "Hello world!")
        )
    print("Data inserted and committed")
```

### Error Handling with Rollback

```python
from database.db_connection import DatabaseConnection, DatabaseConnectionError

try:
    with DatabaseConnection() as db:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO posts ...")
            # If error occurs, transaction is automatically rolled back
except DatabaseConnectionError as e:
    print(f"Database error: {e}")
```

### Using Global Singleton Instance

```python
from database.db_connection import get_db_connection, close_db_connection

# Get global instance (created once, reused everywhere)
db = get_db_connection()

# Use the connection
with db.get_cursor() as cursor:
    cursor.execute("SELECT version()")
    print(cursor.fetchone())

# Close global instance when application shuts down
close_db_connection()
```

### Custom Pool Configuration

```python
from database.db_connection import DatabaseConnection

# Create connection with custom pool size
db = DatabaseConnection(
    min_conn=5,      # Minimum 5 connections
    max_conn=20,     # Maximum 20 connections
    max_retries=5,   # Retry 5 times on failure
    retry_delay=3    # Wait 3 seconds between retries
)
```

### Manual Connection Management

```python
from database.db_connection import DatabaseConnection

db = DatabaseConnection()

# Get connection from pool
conn = db.get_connection()

try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    results = cursor.fetchall()
    cursor.close()
finally:
    # Always return connection to pool
    db.return_connection(conn)
```

## API Reference

### DatabaseConnection Class

#### Constructor

```python
DatabaseConnection(
    min_conn: int = None,      # Minimum connections (default from env)
    max_conn: int = None,      # Maximum connections (default from env)
    max_retries: int = 3,      # Maximum retry attempts
    retry_delay: int = 5       # Delay between retries (seconds)
)
```

#### Methods

- **`get_connection()`**: Get a connection from the pool
- **`return_connection(conn)`**: Return a connection to the pool
- **`get_cursor(commit=False)`**: Context manager for cursor operations
- **`test_connection()`**: Test if database connection is working
- **`close_all_connections()`**: Close all connections in the pool

### Global Functions

- **`get_db_connection()`**: Get or create global database instance (singleton)
- **`close_db_connection()`**: Close global database instance

### Exceptions

- **`DatabaseConnectionError`**: Raised for database connection errors

## Retry Logic

The module implements automatic retry logic for connection failures:

1. **Initial Attempt**: Try to connect to database
2. **Retry on Failure**: If connection fails, wait `retry_delay` seconds and retry
3. **Maximum Attempts**: Retry up to `max_retries` times
4. **Final Failure**: If all attempts fail, raise `DatabaseConnectionError`

Example with 3 retries and 5-second delay:
- Attempt 1: Fails → Wait 5 seconds
- Attempt 2: Fails → Wait 5 seconds
- Attempt 3: Fails → Raise error

## Connection Pooling

The module uses psycopg2's `SimpleConnectionPool` for efficient connection management:

- **Minimum Connections**: Always maintained in the pool
- **Maximum Connections**: Pool can grow up to this limit
- **Connection Reuse**: Connections are reused across requests
- **Automatic Cleanup**: Connections are properly closed on shutdown

Benefits:
- Reduced connection overhead
- Better resource utilization
- Improved performance for concurrent operations

## Error Handling

The module provides comprehensive error handling:

### Configuration Errors

```python
# Missing required configuration
DatabaseConnectionError: Missing required database configuration: DB_HOST, DB_NAME
```

### Connection Errors

```python
# Failed to connect after retries
DatabaseConnectionError: Failed to connect to database after 3 attempts
```

### Operation Errors

```python
# Failed to get connection from pool
DatabaseConnectionError: Failed to get connection: connection refused
```

## Best Practices

1. **Use Context Managers**: Always use `with` statements for automatic cleanup
2. **Commit Explicitly**: Use `commit=True` parameter when modifying data
3. **Handle Errors**: Wrap database operations in try-except blocks
4. **Use Singleton**: Use `get_db_connection()` for application-wide instance
5. **Close on Shutdown**: Call `close_db_connection()` when application exits
6. **Parameterized Queries**: Always use parameterized queries to prevent SQL injection

## Examples

See `examples/db_connection_demo.py` for comprehensive usage examples:

```bash
python examples/db_connection_demo.py
```

## Testing

Run the test suite:

```bash
pytest tests/test_db_connection.py -v
```

## Troubleshooting

### Connection Refused

```
DatabaseConnectionError: Failed to connect to database after 3 attempts
```

**Solutions**:
- Verify PostgreSQL is running
- Check host and port are correct
- Verify firewall allows connections
- Check credentials are correct

### Missing Configuration

```
DatabaseConnectionError: Missing required database configuration: DB_HOST
```

**Solutions**:
- Create `.env` file from `.env.example`
- Set required environment variables
- Verify `.env` file is in project root

### Pool Exhausted

```
DatabaseConnectionError: No connections available in pool
```

**Solutions**:
- Increase `DB_POOL_MAX_CONN` value
- Ensure connections are returned to pool
- Check for connection leaks in code

### Permission Denied

```
psycopg2.OperationalError: FATAL: password authentication failed
```

**Solutions**:
- Verify database credentials
- Check user has required permissions
- Verify database exists

## Related Modules

- **`database/db_operations.py`**: High-level database operations (CRUD)
- **`database/migrations/`**: Database schema migrations
- **`database/scripts/`**: Backup and maintenance scripts

## License

Part of the Social Media Scraper Automation project.
