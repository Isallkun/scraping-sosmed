# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Flask Analytics Dashboard.

## Table of Contents

- [Database Issues](#database-issues)
- [Application Startup Issues](#application-startup-issues)
- [Data Import Issues](#data-import-issues)
- [Performance Issues](#performance-issues)
- [Display Issues](#display-issues)
- [API Issues](#api-issues)
- [Logging and Debugging](#logging-and-debugging)

## Database Issues

### Cannot Connect to Database

**Symptoms**:
- Error: `psycopg2.OperationalError: could not connect to server`
- Dashboard shows "Service Unavailable" error
- Application logs show database connection errors

**Solutions**:

1. **Verify PostgreSQL is running**:
   ```bash
   # Windows
   sc query postgresql-x64-14
   
   # macOS
   brew services list | grep postgresql
   
   # Linux
   sudo systemctl status postgresql
   ```

2. **Start PostgreSQL if stopped**:
   ```bash
   # Windows
   net start postgresql-x64-14
   
   # macOS
   brew services start postgresql@14
   
   # Linux
   sudo systemctl start postgresql
   ```

3. **Check database credentials**:
   - Open `.env` file
   - Verify `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   - Test connection:
     ```bash
     psql -h localhost -p 5432 -U postgres -d social_scraper
     ```

4. **Check PostgreSQL is listening**:
   ```bash
   # Check listening ports
   netstat -an | grep 5432
   
   # Or use psql
   psql -U postgres -c "SHOW port;"
   ```

5. **Check firewall settings**:
   - Ensure port 5432 is not blocked
   - Allow connections from localhost

### Database Tables Don't Exist

**Symptoms**:
- Error: `relation "posts" does not exist`
- API returns empty data
- Dashboard shows no data

**Solutions**:

1. **Run database migrations**:
   ```bash
   python database/scripts/run_migrations.py
   ```

2. **Verify tables exist**:
   ```bash
   psql -U postgres -d social_scraper -c "\dt"
   ```

3. **Check database name**:
   - Ensure you're connected to the correct database
   - Verify `DB_NAME` in `.env` matches the database with tables

### Slow Database Queries

**Symptoms**:
- Dashboard pages load slowly (> 5 seconds)
- API requests timeout
- High CPU usage on database server

**Solutions**:

1. **Check database indexes**:
   ```bash
   psql -U postgres -d social_scraper -c "\di"
   ```

2. **Analyze query performance**:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM posts WHERE timestamp > '2024-01-01';
   ```

3. **Vacuum and analyze database**:
   ```bash
   psql -U postgres -d social_scraper -c "VACUUM ANALYZE;"
   ```

4. **Increase connection pool size**:
   - Edit `.env`:
     ```env
     DB_POOL_MIN=5
     DB_POOL_MAX=20
     ```

5. **Add missing indexes** (if needed):
   ```sql
   CREATE INDEX idx_posts_timestamp ON posts(timestamp);
   CREATE INDEX idx_sentiments_label ON sentiments(label);
   ```

## Application Startup Issues

### Port Already in Use

**Symptoms**:
- Error: `OSError: [Errno 48] Address already in use`
- Flask won't start

**Solutions**:

1. **Find and kill process using port 5000**:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   
   # macOS/Linux
   lsof -ti:5000 | xargs kill -9
   ```

2. **Run Flask on different port**:
   ```bash
   export FLASK_RUN_PORT=5001
   python run_flask.py
   ```

3. **Update `.env` file**:
   ```env
   FLASK_RUN_PORT=5001
   ```

### Module Import Errors

**Symptoms**:
- Error: `ModuleNotFoundError: No module named 'flask'`
- Error: `ImportError: cannot import name 'create_app'`

**Solutions**:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify virtual environment is activated**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Check Python version**:
   ```bash
   python --version  # Should be 3.8 or higher
   ```

4. **Reinstall dependencies**:
   ```bash
   pip install --upgrade --force-reinstall -r requirements.txt
   ```

### Permission Errors

**Symptoms**:
- Error: `PermissionError: [Errno 13] Permission denied`
- Cannot write to logs directory

**Solutions**:

1. **Create logs directory**:
   ```bash
   mkdir -p logs
   chmod 755 logs
   ```

2. **Check file permissions**:
   ```bash
   ls -la logs/
   ```

3. **Run with appropriate permissions**:
   ```bash
   # Linux/macOS
   sudo chown -R $USER:$USER logs/
   ```

## Data Import Issues

### Import Script Fails

**Symptoms**:
- Error: `ValueError: File not found`
- Error: `Invalid JSON format`
- Records are skipped during import

**Solutions**:

1. **Verify file exists**:
   ```bash
   ls -la output/instagram/raw/posts_20260209.json
   ```

2. **Check file format**:
   ```bash
   # Validate JSON
   python -m json.tool output/instagram/raw/posts_20260209.json
   
   # Check CSV headers
   head -n 1 output/instagram/raw/posts_20260209.csv
   ```

3. **Check file permissions**:
   ```bash
   chmod 644 output/instagram/raw/*.json
   ```

4. **Run with verbose logging**:
   ```bash
   python scripts/import_data.py --file output/instagram/raw/posts_20260209.json --verbose
   ```

5. **Check import logs**:
   - Review console output for validation errors
   - Common issues:
     - Missing required fields (post_id, author, timestamp)
     - Invalid timestamp format
     - Corrupted JSON/CSV

### Duplicate Posts

**Symptoms**:
- Same post appears multiple times
- Import shows "updated" but data doesn't change

**Solutions**:

1. **Check post_id uniqueness**:
   ```sql
   SELECT post_id, COUNT(*) 
   FROM posts 
   GROUP BY post_id 
   HAVING COUNT(*) > 1;
   ```

2. **Remove duplicates**:
   ```sql
   DELETE FROM posts 
   WHERE id NOT IN (
     SELECT MIN(id) 
     FROM posts 
     GROUP BY post_id
   );
   ```

3. **Verify upsert logic**:
   - Import script uses `ON CONFLICT (post_id) DO UPDATE`
   - Existing posts should be updated, not duplicated

### Cache Not Invalidated

**Symptoms**:
- Dashboard shows old data after import
- New posts don't appear

**Solutions**:

1. **Manually clear cache**:
   ```python
   from app import create_app, cache
   app = create_app()
   with app.app_context():
       cache.clear()
   ```

2. **Restart Flask application**:
   ```bash
   # Stop Flask (Ctrl+C)
   # Start again
   python run_flask.py
   ```

3. **Check cache configuration**:
   - Verify `CACHE_TYPE` in `.env`
   - For Redis, ensure Redis server is running

## Performance Issues

### Slow Page Load Times

**Symptoms**:
- Pages take > 5 seconds to load
- Charts don't render
- Browser shows "Loading..." indefinitely

**Solutions**:

1. **Check database performance** (see Database Issues above)

2. **Verify cache is working**:
   - Check logs for cache hits/misses
   - Ensure `CACHE_TYPE` is set in `.env`

3. **Reduce data volume**:
   - Use date range filters
   - Limit results per page
   - Archive old data

4. **Enable gzip compression**:
   - Verify Flask-Compress is installed:
     ```bash
     pip install Flask-Compress
     ```

5. **Check network latency**:
   - Test API endpoints directly:
     ```bash
     time curl http://localhost:5000/api/summary
     ```

### High Memory Usage

**Symptoms**:
- Application uses > 1 GB RAM
- System becomes slow
- Out of memory errors

**Solutions**:

1. **Reduce cache size**:
   ```env
   CACHE_DEFAULT_TIMEOUT=60  # Reduce from 300
   ```

2. **Limit query results**:
   - Use pagination
   - Add date range filters
   - Reduce `per_page` parameter

3. **Optimize database queries**:
   - Add indexes
   - Use LIMIT clauses
   - Avoid SELECT *

4. **Restart application periodically**:
   - Use process manager (systemd, supervisor)
   - Implement automatic restarts

## Display Issues

### Charts Don't Render

**Symptoms**:
- Empty chart areas
- Console error: `Chart is not defined`
- Charts show "Loading..." indefinitely

**Solutions**:

1. **Check browser console for errors**:
   - Press F12 to open developer tools
   - Look for JavaScript errors

2. **Verify Chart.js is loaded**:
   - Check network tab in developer tools
   - Ensure Chart.js CDN is accessible

3. **Clear browser cache**:
   - Press Ctrl+Shift+Delete
   - Clear cached images and files

4. **Check API responses**:
   ```bash
   curl http://localhost:5000/api/sentiment
   ```

5. **Verify data format**:
   - API should return valid JSON
   - Check for null or undefined values

### Theme Not Switching

**Symptoms**:
- Theme toggle button doesn't work
- Theme resets on page reload
- Dark mode doesn't apply

**Solutions**:

1. **Check browser localStorage**:
   - Open developer tools (F12)
   - Go to Application > Local Storage
   - Verify `theme` key exists

2. **Clear localStorage**:
   ```javascript
   localStorage.clear();
   location.reload();
   ```

3. **Check JavaScript errors**:
   - Open browser console
   - Look for errors in `common.js`

4. **Verify CSS is loaded**:
   - Check network tab
   - Ensure `style.css` loads successfully

### Mobile Display Issues

**Symptoms**:
- Layout broken on mobile
- Charts overflow screen
- Navigation menu doesn't work

**Solutions**:

1. **Check viewport meta tag**:
   - Verify `<meta name="viewport">` in `base.html`

2. **Test responsive design**:
   - Use browser developer tools
   - Toggle device toolbar (Ctrl+Shift+M)

3. **Clear mobile browser cache**:
   - Settings > Clear browsing data

4. **Check Tailwind CSS**:
   - Verify Tailwind CDN is accessible
   - Check for CSS conflicts

## API Issues

### API Returns Empty Data

**Symptoms**:
- API endpoint returns `[]` or `{}`
- Dashboard shows "No data available"

**Solutions**:

1. **Verify data exists in database**:
   ```sql
   SELECT COUNT(*) FROM posts;
   SELECT COUNT(*) FROM sentiments;
   ```

2. **Check date filters**:
   - Remove date range parameters
   - Verify date format (ISO 8601)

3. **Check API logs**:
   - Review `logs/flask_dashboard.log`
   - Look for query errors

4. **Test API directly**:
   ```bash
   curl http://localhost:5000/api/summary
   curl http://localhost:5000/api/posts?page=1&per_page=10
   ```

### API Returns 400 Bad Request

**Symptoms**:
- Error: `Invalid date format`
- Error: `Invalid parameter value`

**Solutions**:

1. **Check parameter format**:
   - Dates: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`
   - Numbers: Integer values only
   - Strings: URL-encoded

2. **Verify parameter names**:
   - Use correct parameter names (see API docs)
   - Check for typos

3. **Test with minimal parameters**:
   ```bash
   # Start simple
   curl http://localhost:5000/api/posts
   
   # Add parameters one at a time
   curl "http://localhost:5000/api/posts?page=1"
   curl "http://localhost:5000/api/posts?page=1&per_page=10"
   ```

### CORS Errors

**Symptoms**:
- Browser console: `CORS policy: No 'Access-Control-Allow-Origin' header`
- API works in curl but not in browser

**Solutions**:

1. **Verify Flask-CORS is installed**:
   ```bash
   pip install Flask-CORS
   ```

2. **Check CORS configuration**:
   - Verify `CORS(app)` in `app/__init__.py`

3. **Test with curl**:
   ```bash
   curl -H "Origin: http://example.com" \
        -H "Access-Control-Request-Method: GET" \
        -X OPTIONS \
        http://localhost:5000/api/summary
   ```

## Logging and Debugging

### Enable Debug Mode

```bash
# Set in .env
DEBUG=True

# Or export environment variable
export DEBUG=True
python run_flask.py
```

### View Application Logs

```bash
# View recent logs
tail -f logs/flask_dashboard.log

# View all logs
cat logs/flask_dashboard.log

# Search logs for errors
grep ERROR logs/flask_dashboard.log
```

### Enable Verbose Logging

```python
# In app/__init__.py
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### Database Query Logging

```python
# Enable in .env
DEBUG=True

# Queries will be logged to console and log file
```

### Check System Resources

```bash
# Check disk space
df -h

# Check memory usage
free -m

# Check CPU usage
top

# Check PostgreSQL processes
ps aux | grep postgres
```

## Getting Help

If you can't resolve the issue:

1. **Collect information**:
   - Error messages
   - Application logs
   - Database logs
   - System information

2. **Check documentation**:
   - [Installation Guide](INSTALLATION.md)
   - [Usage Guide](USAGE.md)
   - [API Documentation](API.md)

3. **Review logs**:
   - `logs/flask_dashboard.log`
   - PostgreSQL logs
   - Browser console

4. **Test components individually**:
   - Database connection
   - API endpoints
   - Frontend rendering

## Common Error Messages

### `relation "posts" does not exist`
**Solution**: Run database migrations

### `could not connect to server`
**Solution**: Start PostgreSQL service

### `Address already in use`
**Solution**: Kill process on port 5000 or use different port

### `ModuleNotFoundError`
**Solution**: Install dependencies with pip

### `PermissionError`
**Solution**: Check file permissions and create logs directory

### `Invalid JSON format`
**Solution**: Validate JSON file format

### `Cache backend unavailable`
**Solution**: Use simple cache or start Redis

### `Chart is not defined`
**Solution**: Check Chart.js CDN and browser console

## Prevention Tips

1. **Regular backups**: Backup database regularly
2. **Monitor logs**: Check logs for warnings
3. **Update dependencies**: Keep packages up to date
4. **Test imports**: Validate data before importing
5. **Use version control**: Track configuration changes
6. **Document changes**: Keep notes on customizations
7. **Monitor performance**: Track page load times
8. **Clean old data**: Archive or delete old posts

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
