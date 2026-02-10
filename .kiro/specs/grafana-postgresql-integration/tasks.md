# Implementation Plan: Grafana-PostgreSQL Integration

## Overview

This implementation plan breaks down the Grafana-PostgreSQL integration into discrete, incremental tasks. The approach follows this sequence:

1. Set up project structure and dependencies
2. Implement data import script with validation and error handling
3. Create Grafana provisioning configuration for manual setup
4. Download and configure Grafana for Windows
5. Provision Grafana dashboards and data sources
6. Create SQL query library
7. Write documentation

Each task builds on previous work, with checkpoints to ensure functionality before proceeding. The setup uses the existing local PostgreSQL database and a standalone Grafana installation on Windows.

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create directory structure for import scripts, Grafana provisioning configs, and dashboards
  - Create requirements.txt with dependencies: psycopg2-binary, pandas, python-dotenv, hypothesis (for testing)
  - Create .env.example file with local database configuration variables
  - _Requirements: 1.1, 3.1, 9.1_

- [ ] 2. Implement core data validation module
  - [ ] 2.1 Create validation.py with validation functions
    - Implement validate_post_record() to check required fields (post_id, platform, author, content, timestamp)
    - Implement validate_sentiment_record() to check score ranges (-1 to 1)
    - Implement validate_timestamp() to check ISO 8601 format
    - Implement validate_engagement_metrics() to check non-negative integers
    - _Requirements: 11.1, 11.2, 11.3, 11.6_
  
  - [ ]* 2.2 Write property test for data validation
    - **Property 7: Data Validation Completeness**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.6**
  
  - [ ] 2.3 Implement data normalization functions
    - Implement normalize_timestamp() to convert various formats to datetime
    - Implement normalize_hashtags() to remove # prefix and lowercase
    - _Requirements: 11.5_
  
  - [ ]* 2.4 Write property test for hashtag normalization
    - **Property 8: Hashtag Normalization**
    - **Validates: Requirements 11.5**

- [ ] 3. Implement data import core functionality
  - [ ] 3.1 Create import_data.py with DataImporter class
    - Implement __init__() with database connection, batch_size, and incremental mode parameters
    - Implement _process_json() to parse JSON structure and extract PostRecord objects
    - Implement _process_csv() to parse CSV and extract PostRecord objects
    - _Requirements: 1.1, 1.7, 1.8_
  
  - [ ]* 3.2 Write property test for import completeness
    - **Property 1: Data Import Completeness**
    - **Validates: Requirements 1.1, 1.7, 1.8**
  
  - [ ] 3.3 Implement batch insert logic
    - Implement _batch_insert_posts() using existing db_operations.insert_post()
    - Implement _insert_sentiments() using existing db_operations.insert_sentiment()
    - Use batch size of 50 records with transaction commits
    - _Requirements: 1.2, 1.3, 12.1, 12.2_
  
  - [ ]* 3.4 Write property test for upsert consistency
    - **Property 2: Upsert Consistency**
    - **Validates: Requirements 1.2, 2.1, 2.2**
  
  - [ ]* 3.5 Write property test for foreign key integrity
    - **Property 3: Foreign Key Integrity**
    - **Validates: Requirements 1.3**

- [ ] 4. Implement progress reporting and summary
  - [ ] 4.1 Add progress tracking to DataImporter
    - Implement progress reporting every 10 records
    - Track counts: total_processed, inserted, updated, skipped, failed
    - Implement _generate_summary() to create ImportResult
    - _Requirements: 1.4, 1.6, 2.3_
  
  - [ ]* 4.2 Write property test for summary accuracy
    - **Property 4: Import Summary Accuracy**
    - **Validates: Requirements 1.6, 2.3**

- [ ] 5. Implement error handling and logging
  - [ ] 5.1 Add comprehensive error handling
    - Implement connection retry logic with exponential backoff (3 retries: 1s, 2s, 4s)
    - Catch and log JSON parsing errors with file name and line number
    - Catch and log database errors (foreign key violations, constraint violations)
    - Continue processing after errors (skip problematic records)
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [ ]* 5.2 Write property test for error resilience
    - **Property 5: Error Resilience**
    - **Validates: Requirements 1.5, 10.3, 10.6**
  
  - [ ]* 5.3 Write property test for connection retry logic
    - **Property 9: Connection Retry Logic**
    - **Validates: Requirements 10.1**
  
  - [ ] 5.4 Implement logging configuration
    - Configure logging to write to both console (INFO level) and file (DEBUG level)
    - Log file format: logs/import_YYYYMMDD_HHMMSS.log
    - Include full stack traces in file logs
    - Log execution time and performance metrics
    - _Requirements: 10.5, 10.6, 10.7_
  
  - [ ]* 5.5 Write property test for error logging detail
    - **Property 10: Error Logging Detail**
    - **Validates: Requirements 10.2, 10.6**

- [ ] 6. Implement duplicate detection and incremental mode
  - [ ] 6.1 Add duplicate detection within batches
    - Track seen post_ids within current import batch
    - Skip duplicates and log warnings
    - _Requirements: 1.9_
  
  - [ ] 6.2 Implement incremental import mode
    - Check existing post_ids before inserting
    - Compare timestamps and update only if newer
    - Track and report skipped records
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ] 6.3 Add comment deduplication logic
    - Detect duplicate comments by author + timestamp combination
    - Skip duplicate comments
    - _Requirements: 2.4_
  
  - [ ]* 6.4 Write property test for duplicate detection
    - **Property 6: Duplicate Detection**
    - **Validates: Requirements 1.9, 2.4**

- [ ] 7. Implement file and directory processing
  - [ ] 7.1 Implement import_file() method
    - Detect file type (JSON or CSV)
    - Call appropriate processing method
    - Return ImportResult
    - _Requirements: 1.1, 1.8_
  
  - [ ] 7.2 Implement import_directory() method
    - Scan directory for JSON and CSV files
    - Process each file sequentially
    - Aggregate results from all files
    - _Requirements: 1.7_
  
  - [ ] 7.3 Add CLI interface with argparse
    - Support --file and --directory arguments
    - Support --incremental flag
    - Support --batch-size parameter
    - Display summary after completion
    - _Requirements: 1.1, 1.7, 2.1_

- [ ] 8. Checkpoint - Test import script with sample data
  - Run import script with sample JSON files from output/instagram/
  - Verify data appears in local PostgreSQL database
  - Check logs for errors
  - Ensure all tests pass, ask the user if questions arise

- [ ] 9. Create Grafana provisioning configuration
  - [ ] 9.1 Create data source provisioning file
    - Create grafana/provisioning/datasources/postgres.yml
    - Configure PostgreSQL connection to localhost:5432
    - Use local database credentials
    - Set as default data source
    - _Requirements: 3.1, 3.4, 3.5_
  
  - [ ] 9.2 Create dashboard provisioning file
    - Create grafana/provisioning/dashboards/default.yml
    - Configure dashboard folder and auto-loading
    - Set path to local dashboard directory
    - _Requirements: 3.4, 3.6_
  
  - [ ]* 9.3 Write property test for provisioning validation
    - **Property 11: Grafana Provisioning Validation**
    - **Validates: Requirements 3.4, 3.6**

- [ ] 10. Set up Grafana for Windows
  - [ ] 10.1 Create Grafana setup guide
    - Document download URL: https://grafana.com/grafana/download?platform=windows
    - Document extraction location (e.g., C:\grafana\)
    - Document directory structure for provisioning files
    - _Requirements: 3.2, 9.1, 9.7_
  
  - [ ] 10.2 Create provisioning setup script
    - Create script to copy provisioning files to Grafana installation
    - Copy grafana/provisioning/ to C:\grafana\conf\provisioning\
    - Copy grafana/dashboards/ to C:\grafana\dashboards\
    - _Requirements: 3.4, 3.6_
  
  - [ ] 10.3 Document Grafana startup process
    - Document how to run grafana-server.exe
    - Document accessing Grafana at http://localhost:3000
    - Document default credentials (admin/admin)
    - _Requirements: 3.3, 9.7_

- [ ] 11. Create Sentiment Overview Dashboard
  - [ ] 11.1 Create dashboard JSON definition
    - Create grafana/dashboards/sentiment-overview.json
    - Configure dashboard metadata and variables
    - Set default time range to last 30 days
    - _Requirements: 4.1, 4.5_
  
  - [ ]* 11.2 Write property test for panel configuration
    - **Property 12: Dashboard Panel Configuration**
    - **Validates: Requirements 4.4**
  
  - [ ] 11.3 Add sentiment distribution pie chart panel
    - Query: SELECT label, COUNT(*) FROM sentiments GROUP BY label
    - Configure pie chart visualization
    - _Requirements: 5.1_
  
  - [ ] 11.4 Add sentiment trend line chart panel
    - Query: Aggregate sentiment by day with DATE_TRUNC
    - Configure time series visualization
    - Add date range filter support
    - _Requirements: 5.2, 5.5_
  
  - [ ]* 11.5 Write property test for date range filter consistency
    - **Property 13: Date Range Filter Consistency**
    - **Validates: Requirements 5.5, 7.5**
  
  - [ ]* 11.6 Write property test for sentiment aggregation logic
    - **Property 14: Sentiment Aggregation Logic**
    - **Validates: Requirements 5.6**
  
  - [ ] 11.7 Add average sentiment gauge panel
    - Query: SELECT AVG(compound) FROM sentiments
    - Configure gauge visualization (-1 to 1 range)
    - _Requirements: 5.3_
  
  - [ ] 11.8 Add sentiment by post type panel
    - Query: Join posts and sentiments, group by media_type and label
    - Configure stacked bar chart
    - _Requirements: 5.1_

- [ ] 12. Create Engagement Metrics Dashboard
  - [ ] 12.1 Create dashboard JSON definition
    - Create grafana/dashboards/engagement-metrics.json
    - Configure dashboard metadata and variables
    - Set default time range to last 30 days
    - _Requirements: 4.2, 4.5_
  
  - [ ] 12.2 Add total posts/reels stat panels
    - Query: COUNT with FILTER for post types
    - Configure stat panel visualizations
    - _Requirements: 6.1_
  
  - [ ] 12.3 Add top posts table panel
    - Query: Order by total engagement DESC, LIMIT 10
    - Configure table visualization with columns
    - _Requirements: 6.2_
  
  - [ ]* 12.4 Write property test for top posts ranking
    - **Property 15: Top Posts Ranking Correctness**
    - **Validates: Requirements 6.2, 8.2**
  
  - [ ] 12.5 Add engagement rate over time panel
    - Query: Calculate average engagement by day
    - Configure time series line chart
    - _Requirements: 6.3, 6.6_
  
  - [ ]* 12.6 Write property test for engagement rate calculation
    - **Property 16: Engagement Rate Calculation**
    - **Validates: Requirements 6.6, 8.6**
  
  - [ ] 12.7 Add post type distribution pie chart
    - Query: SELECT media_type, COUNT(*) GROUP BY media_type
    - Configure pie chart visualization
    - _Requirements: 6.4_

- [ ] 13. Create Content Analysis Dashboard
  - [ ] 13.1 Create dashboard JSON definition
    - Create grafana/dashboards/content-analysis.json
    - Configure dashboard metadata and variables
    - Set default time range to last 30 days
    - _Requirements: 4.3, 4.5_
  
  - [ ] 13.2 Add top hashtags bar chart panel
    - Query: UNNEST hashtags, count frequency, filter >= 3, LIMIT 20
    - Configure horizontal bar chart
    - _Requirements: 7.1, 7.6_
  
  - [ ]* 13.3 Write property test for hashtag frequency filtering
    - **Property 17: Hashtag Frequency Filtering**
    - **Validates: Requirements 7.6**
  
  - [ ]* 13.4 Write property test for top hashtags ranking
    - **Property 18: Top Hashtags Ranking Correctness**
    - **Validates: Requirements 7.1, 8.5**
  
  - [ ] 13.5 Add posting frequency heatmap panel
    - Query: Extract day of week and hour, count posts
    - Configure heatmap visualization
    - _Requirements: 7.2_
  
  - [ ] 13.6 Add average comments stat panel
    - Query: SELECT AVG(comments_count) FROM posts
    - Configure stat panel
    - _Requirements: 7.3_
  
  - [ ]* 13.7 Write property test for average comments calculation
    - **Property 22: Average Comments Calculation**
    - **Validates: Requirements 7.3**
  
  - [ ] 13.8 Add content length distribution panel
    - Query: Categorize by LENGTH(content), count by category
    - Configure bar chart
    - _Requirements: 7.4_

- [ ] 14. Checkpoint - Test dashboards with sample data
  - Download and extract Grafana for Windows
  - Copy provisioning files to Grafana installation directory
  - Start Grafana executable
  - Import sample data using import script to local PostgreSQL
  - Open Grafana at http://localhost:3000
  - Verify all three dashboards load correctly
  - Verify all panels display data
  - Test date range filters
  - Ensure all tests pass, ask the user if questions arise

- [ ] 15. Create SQL query library
  - [ ] 15.1 Create sql_queries/analytics_queries.sql
    - Add sentiment distribution query with date range parameters
    - Add top posts by engagement query with limit parameter
    - Add daily post counts query with date range parameters
    - Add sentiment trends query with date range parameters
    - Add hashtag frequency analysis query
    - Add engagement rate calculation query
    - Add posting time analysis query
    - Add content performance by length query
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  
  - [ ]* 15.2 Write property test for daily post count accuracy
    - **Property 19: Daily Post Count Accuracy**
    - **Validates: Requirements 8.3**
  
  - [ ]* 15.3 Write property test for sentiment trend calculation
    - **Property 20: Sentiment Trend Calculation**
    - **Validates: Requirements 8.4**
  
  - [ ]* 15.4 Write property test for SQL injection prevention
    - **Property 21: SQL Injection Prevention**
    - **Validates: Requirements 8.7**
  
  - [ ] 15.5 Add query documentation
    - Document each query's purpose and parameters
    - Include example usage
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ] 16. Create comprehensive documentation
  - [ ] 16.1 Create GRAFANA_SETUP.md
    - Write prerequisites section (Grafana for Windows, Python 3.8+, local PostgreSQL)
    - Write step-by-step setup instructions for Windows
    - Include Grafana download and extraction steps
    - Include provisioning file setup instructions
    - Include Grafana startup commands
    - Add troubleshooting section for common issues
    - _Requirements: 9.1, 9.7_
  
  - [ ] 16.2 Create IMPORT_GUIDE.md
    - Document import script usage with examples
    - Include single file import example
    - Include directory batch import example
    - Include incremental mode example
    - Document command-line arguments
    - Add troubleshooting section
    - _Requirements: 9.2, 9.6_
  
  - [ ] 16.3 Create DASHBOARD_CUSTOMIZATION.md
    - Document how to customize existing dashboards
    - Explain dashboard JSON structure
    - Document how to add new panels
    - Document how to modify queries
    - Include examples of common customizations
    - _Requirements: 9.3_
  
  - [ ] 16.4 Update main README.md
    - Add Grafana integration section
    - Link to setup and usage guides
    - Add screenshots of dashboards
    - Include quick start guide for manual setup
    - _Requirements: 9.1_

- [ ] 17. Final checkpoint - End-to-end validation
  - Stop Grafana if running
  - Follow setup guide to configure environment from scratch
  - Download and extract fresh Grafana installation
  - Copy provisioning files to Grafana directories
  - Start Grafana
  - Import real Instagram data from output/ directory to local PostgreSQL
  - Verify all dashboards display correct data
  - Test all date range filters
  - Test incremental import with new data
  - Verify Grafana loads dashboards on restart
  - Run all property-based tests
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The import script leverages existing database operations from database/db_operations.py
- Manual setup uses existing local PostgreSQL from database/ directory
- Grafana runs as standalone Windows executable without Docker
- All dashboards use parameterized queries for security and flexibility
