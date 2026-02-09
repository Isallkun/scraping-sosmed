# Implementation Plan: Social Media Scraper Automation

## Overview

Implementasi sistem otomasi scraping sosial media dengan analisis sentimen menggunakan Python, Selenium, n8n, dan PostgreSQL. Sistem akan di-deploy menggunakan Docker Compose untuk portability dan scalability. Implementation plan ini dibagi menjadi beberapa fase: setup project, implementasi scraper, sentiment analyzer, database, n8n workflows, Docker deployment, dan testing.

## Tasks

- [x] 1. Project Setup and Infrastructure
  - Create project directory structure
  - Initialize Python virtual environment
  - Create requirements.txt with dependencies: selenium, beautifulsoup4, pandas, vaderSentiment, textblob, psycopg2-binary, python-dotenv
  - Create .env.example with all required environment variables documented
  - Create .gitignore for Python, Docker, and IDE files
  - _Requirements: 8.6_

- [ ] 2. Implement Base Scraper Infrastructure
  - [x] 2.1 Create scraper module structure (scraper/__init__.py, main_scraper.py, config.py)
    - Set up package structure with proper imports
    - _Requirements: 1.1, 1.5_
  
  - [x] 2.2 Implement configuration management (config.py)
    - Load environment variables using python-dotenv
    - Validate required configuration variables
    - Raise descriptive errors for missing variables
    - _Requirements: 8.1, 8.4_
  
  - [ ]* 2.3 Write property test for configuration loading
    - **Property 14: Configuration Loading Correctness**
    - **Validates: Requirements 8.1, 8.2**
  
  - [ ]* 2.4 Write property test for missing configuration errors
    - **Property 15: Missing Configuration Error Messages**
    - **Validates: Requirements 8.4**
  
  - [x] 2.5 Implement logging utilities (scraper/utils/logger.py)
    - Configure rotating file handler with size/time limits
    - Set up log format with timestamp, level, component, message
    - Implement credential sanitization for log output
    - _Requirements: 9.1, 9.2, 9.3, 9.7, 8.5_
  
  - [ ]* 2.6 Write property test for log entry format
    - **Property 17: Log Entry Format Completeness**
    - **Validates: Requirements 9.1, 9.7**
  
  - [ ]* 2.7 Write property test for credential sanitization
    - **Property 16: Credential Sanitization in Logs**
    - **Validates: Requirements 8.5**
  
  - [ ]* 2.8 Write property test for log file rotation
    - **Property 19: Log File Rotation**
    - **Validates: Requirements 9.3**

- [ ] 3. Implement Anti-Detection and Rate Limiting
  - [x] 3.1 Create anti-detection utilities (scraper/utils/anti_detection.py)
    - Implement random user agent selection from list of valid browser user agents
    - Implement random viewport size generation
    - Implement human-like delay with random jitter
    - _Requirements: 1.4, 10.3_
  
  - [ ]* 3.2 Write property test for anti-detection randomization
    - **Property 3: Anti-Detection Randomization**
    - **Validates: Requirements 1.4**
  
  - [ ]* 3.3 Write property test for user agent configuration
    - **Property 21: User Agent Configuration**
    - **Validates: Requirements 10.3**
  
  - [x] 3.4 Implement rate limiter (scraper/utils/rate_limiter.py)
    - Implement token bucket algorithm for rate limiting
    - Make requests per minute configurable
    - _Requirements: 1.3, 10.2_
  
  - [ ]* 3.5 Write property test for rate limiting enforcement
    - **Property 2: Rate Limiting Enforcement**
    - **Validates: Requirements 1.3, 10.2**

- [ ] 4. Implement Base Scraper Class
  - [x] 4.1 Create abstract base scraper (scraper/scrapers/base_scraper.py)
    - Define abstract methods: authenticate(), scrape_posts(), extract_post_data()
    - Implement common functionality: WebDriver setup, rate limiting, timeout enforcement
    - Implement retry logic with exponential backoff for network errors
    - Implement error handling and logging
    - _Requirements: 1.1, 1.8, 11.1, 11.5_
  
  - [ ]* 4.2 Write property test for timeout enforcement
    - **Property 5: Scraper Timeout Enforcement**
    - **Validates: Requirements 1.8**
  
  - [ ]* 4.3 Write property test for retry logic
    - **Property 22: Retry Logic with Maximum Attempts**
    - **Validates: Requirements 11.1**
  
  - [ ]* 4.4 Write property test for exception handling
    - **Property 23: Exception Handling Graceful Failure**
    - **Validates: Requirements 11.5**

- [ ] 5. Implement Platform-Specific Scrapers
  - [x] 5.1 Implement Instagram scraper (scraper/scrapers/instagram.py)
    - Implement authenticate() method with Instagram login flow
    - Implement scrape_posts() to navigate and extract posts
    - Implement extract_post_data() to parse post elements
    - Extract: post_id, author, content, timestamp, likes, comments_count, hashtags
    - Handle pagination and scrolling
    - _Requirements: 1.1, 1.2_
  
  - [x] 5.2 Implement Twitter scraper (scraper/scrapers/twitter.py)
    - Implement authenticate() method with Twitter login flow
    - Implement scrape_posts() to navigate and extract tweets
    - Implement extract_post_data() to parse tweet elements
    - Extract: post_id, author, content, timestamp, likes, retweets, replies
    - _Requirements: 1.1, 1.2_
  
  - [x] 5.3 Implement Facebook scraper (scraper/scrapers/facebook.py)
    - Implement authenticate() method with Facebook login flow
    - Implement scrape_posts() to navigate and extract posts
    - Implement extract_post_data() to parse post elements
    - Extract: post_id, author, content, timestamp, likes, comments_count, shares
    - _Requirements: 1.1, 1.2_
  
  - [ ]* 5.4 Write property test for scraped data completeness
    - **Property 1: Scraped Data Completeness**
    - **Validates: Requirements 1.2**

- [ ] 6. Implement Scraper CLI and Output
  - [x] 6.1 Create main scraper CLI (scraper/main_scraper.py)
    - Implement argument parser for platform, target URL, limit, output path, format
    - Instantiate appropriate scraper based on platform
    - Execute scraping workflow
    - Handle errors and exit codes
    - _Requirements: 1.6, 11.2_
  
  - [x] 6.2 Implement JSON output formatter
    - Create output structure with metadata and posts array
    - Write to file with proper formatting
    - Implement partial data persistence (save successful posts even if errors occur)
    - _Requirements: 1.5, 11.6_
  
  - [ ]* 6.3 Write property test for output schema validity
    - **Property 4: Scraper Output Schema Validity**
    - **Validates: Requirements 1.5**
  
  - [ ]* 6.4 Write property test for partial data persistence
    - **Property 24: Partial Data Persistence**
    - **Validates: Requirements 11.6**
  
  - [x] 6.5 Write unit tests for CLI argument parsing
    - Test various argument combinations
    - Test error handling for invalid arguments
    - _Requirements: 1.6_

- [x] 7. Checkpoint - Test Scraper Components
  - Ensure all scraper tests pass, ask the user if questions arise.

- [ ] 8. Implement Sentiment Analysis Module
  - [x] 8.1 Create sentiment analyzer structure (sentiment/__init__.py, sentiment_analyzer.py, text_cleaner.py)
    - Set up package structure with proper imports
    - _Requirements: 2.1_
  
  - [x] 8.2 Implement text cleaner (sentiment/text_cleaner.py)
    - Implement remove_urls() to strip http/https/www URLs
    - Implement normalize_whitespace() to collapse multiple spaces
    - Implement clean() to apply all cleaning steps
    - _Requirements: 2.2_
  
  - [ ]* 8.3 Write property test for text cleaning
    - **Property 6: Text Cleaning Removes URLs**
    - **Validates: Requirements 2.2**
  
  - [x] 8.4 Implement VADER sentiment model (sentiment/models/vader_model.py)
    - Initialize VADER SentimentIntensityAnalyzer
    - Implement analyze() method to return scores and label
    - Apply classification thresholds (>=0.05 positive, <=-0.05 negative)
    - _Requirements: 2.3, 2.4_
  
  - [x] 8.5 Implement TextBlob sentiment model (sentiment/models/textblob_model.py)
    - Initialize TextBlob analyzer
    - Implement analyze() method to return scores and label
    - Normalize TextBlob scores to match VADER format
    - _Requirements: 2.3, 2.4_
  
  - [ ]* 8.6 Write property test for sentiment score validity
    - **Property 7: Sentiment Score Validity**
    - **Validates: Requirements 2.3**
  
  - [ ]* 8.7 Write property test for sentiment classification consistency
    - **Property 8: Sentiment Classification Consistency**
    - **Validates: Requirements 2.4**

- [ ] 9. Implement Sentiment Analyzer Orchestrator
  - [x] 9.1 Create main sentiment analyzer class (sentiment/sentiment_analyzer.py)
    - Implement __init__ with model selection (vader/textblob) and batch size
    - Implement analyze_file() to read input, process, write output
    - Implement analyze_batch() for batch processing
    - Implement analyze_single() for single text analysis
    - Handle errors gracefully, continue processing on individual failures
    - _Requirements: 2.1, 2.5, 2.6, 2.7_
  
  - [ ]* 9.2 Write property test for data enrichment
    - **Property 9: Data Enrichment Preserves Original Fields**
    - **Validates: Requirements 2.5**
  
  - [ ]* 9.3 Write property test for batch processing completeness
    - **Property 10: Batch Processing Completeness**
    - **Validates: Requirements 2.6**
  
  - [ ]* 9.4 Write property test for partial failure resilience
    - **Property 11: Partial Failure Resilience**
    - **Validates: Requirements 2.7**
  
  - [x] 9.5 Create sentiment analyzer CLI
    - Implement argument parser for input, output, model, batch-size
    - Execute analysis workflow
    - Handle errors and exit codes
    - _Requirements: 2.1_
  
  - [x] 9.6 Write unit tests for sentiment analyzer CLI
    - Test argument parsing
    - Test file I/O error handling
    - _Requirements: 2.1_

- [x] 10. Checkpoint - Test Sentiment Analysis Components
  - Ensure all sentiment analysis tests pass, ask the user if questions arise.

- [ ] 11. Implement Database Schema and Migrations
  - [x] 11.1 Create database directory structure (database/migrations/, database/scripts/)
    - Set up directory for SQL files
    - _Requirements: 6.1_
  
  - [x] 11.2 Create initial schema migration (database/migrations/001_initial_schema.sql)
    - Create posts table with all fields and indexes
    - Create sentiments table with foreign key to posts
    - Create execution_logs table
    - Create updated_at trigger function
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.6_
  
  - [x] 11.3 Create database connection module (database/db_connection.py)
    - Implement connection pooling with psycopg2
    - Load connection string from environment variables
    - Implement retry logic for connection failures
    - _Requirements: 8.3, 11.3_
  
  - [x] 11.4 Implement database operations (database/db_operations.py)
    - Implement insert_post() with upsert logic (ON CONFLICT UPDATE)
    - Implement insert_sentiment() with foreign key handling
    - Implement insert_execution_log()
    - Implement query methods for reports
    - Use parameterized queries to prevent SQL injection
    - _Requirements: 6.2, 6.3, 6.4, 6.5, 10.4_
  
  - [ ]* 11.5 Write property test for database round-trip consistency
    - **Property 12: Database Round-Trip Consistency**
    - **Validates: Requirements 6.2, 6.3, 6.4**
  
  - [ ]* 11.6 Write property test for duplicate post upsert
    - **Property 13: Duplicate Post Upsert Behavior**
    - **Validates: Requirements 6.5**
  
  - [x] 11.7 Write unit tests for database operations
    - Test insert, update, query operations
    - Test error handling for constraint violations
    - _Requirements: 6.2, 6.3, 6.4, 6.5_

- [ ] 12. Implement Backup and Data Retention
  - [~] 12.1 Create backup script (database/scripts/backup.sh)
    - Use pg_dump to create timestamped backup
    - Store backup in designated directory
    - Verify backup integrity by checking file size and readability
    - Log backup success/failure
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [ ]* 12.2 Write property test for backup file creation
    - **Property 25: Backup File Creation with Timestamp**
    - **Validates: Requirements 12.1**
  
  - [ ]* 12.3 Write property test for backup storage location
    - **Property 26: Backup Storage Location**
    - **Validates: Requirements 12.2**
  
  - [ ]* 12.4 Write property test for backup integrity verification
    - **Property 27: Backup Integrity Verification**
    - **Validates: Requirements 12.3**
  
  - [~] 12.5 Create backup retention script (database/scripts/cleanup_old_backups.sh)
    - Implement retention policy: 7 daily, 4 weekly, 3 monthly
    - Delete backups older than retention period
    - Log cleanup operations
    - _Requirements: 12.4_
  
  - [ ]* 12.6 Write property test for backup retention policy
    - **Property 28: Backup Retention Policy Enforcement**
    - **Validates: Requirements 12.4**
  
  - [~] 12.7 Create restore documentation (database/RESTORE.md)
    - Document step-by-step restore procedure
    - Include examples for point-in-time recovery
    - _Requirements: 12.5, 12.6_
  
  - [~] 12.8 Create data retention script (database/scripts/cleanup_old_data.sql)
    - Delete posts older than 90 days
    - Delete execution logs older than 30 days
    - _Requirements: 6.7_

- [ ] 13. Implement Health Check and Monitoring
  - [~] 13.1 Create health check script (scripts/health_check.py)
    - Check database connectivity
    - Check scraper service status
    - Check disk space for logs and backups
    - Return JSON response with status and timestamp
    - _Requirements: 9.5_
  
  - [ ]* 13.2 Write property test for health check response
    - **Property 20: Health Check Response Validity**
    - **Validates: Requirements 9.5**
  
  - [~] 13.3 Implement notification utilities (scripts/notify.py)
    - Implement send_email() for email notifications
    - Implement send_slack() for Slack notifications
    - Implement send_telegram() for Telegram notifications
    - Load notification credentials from environment variables
    - _Requirements: 3.7, 9.6_

- [ ] 14. Create n8n Workflow Configurations
  - [~] 14.1 Create n8n workflows directory (n8n/workflows/)
    - Set up directory for workflow JSON exports
    - _Requirements: 3.1_
  
  - [~] 14.2 Design Daily Scraping Workflow (n8n/workflows/daily_scraping.json)
    - Create Cron Trigger node (schedule: 0 2 * * *)
    - Create Execute Command node for scraper
    - Create IF node to check scraper exit code
    - Create Execute Command node for sentiment analyzer
    - Create Read Binary File nodes for JSON outputs
    - Create PostgreSQL nodes for data insertion
    - Create Function node for summary generation
    - Create Email/Slack notification nodes
    - Create error handling branches
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_
  
  - [~] 14.3 Design On-Demand Webhook Workflow (n8n/workflows/webhook_scraping.json)
    - Create Webhook Trigger node (POST /webhook/scrape)
    - Create Function node for payload validation
    - Create IF node for validation result
    - Create Execute Command nodes for scraper and analyzer
    - Create Respond to Webhook node with JSON response
    - Create PostgreSQL node for logging
    - Create error response handling
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [~] 14.4 Design Weekly Report Workflow (n8n/workflows/weekly_report.json)
    - Create Cron Trigger node (schedule: 0 9 * * 0)
    - Create PostgreSQL Query nodes for data retrieval
    - Create Function node for metrics aggregation
    - Create HTTP Request node for chart generation
    - Create Function node for report formatting
    - Create Email node with PDF attachment
    - Create PostgreSQL node for logging
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [~] 14.5 Create n8n environment variables template (n8n/.env.n8n.example)
    - Document all required n8n environment variables
    - Include database connection strings
    - Include notification service credentials
    - _Requirements: 8.3_
  
  - [~] 14.6 Create workflow documentation (n8n/WORKFLOWS.md)
    - Document each workflow's purpose and configuration
    - Include setup instructions
    - Document webhook endpoints and payloads
    - _Requirements: 3.1, 4.1, 5.1_

- [ ] 15. Implement Docker Configuration
  - [~] 15.1 Create Dockerfile for Python scraper (Dockerfile)
    - Use Python 3.11 slim base image
    - Install system dependencies (chromium, chromedriver)
    - Copy application code
    - Install Python dependencies from requirements.txt
    - Create non-root user for running application
    - Set working directory and entrypoint
    - _Requirements: 7.6, 10.5_
  
  - [~] 15.2 Create Docker Compose configuration (docker-compose.yml)
    - Define services: n8n, postgres, redis (optional), scraper
    - Configure networks for inter-service communication
    - Configure volumes for persistent data (postgres data, n8n data, logs, backups)
    - Set environment variables from .env file
    - Configure health checks for each service
    - Set restart policies
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.7_
  
  - [~] 15.3 Create main .env.example file
    - Combine all environment variables from scraper, sentiment, database, n8n
    - Document each variable with description and example value
    - Group variables by component
    - _Requirements: 7.4, 8.6_
  
  - [~] 15.4 Create Docker setup script (scripts/setup.sh)
    - Check Docker and Docker Compose installation
    - Copy .env.example to .env if not exists
    - Prompt user to edit .env file
    - Run docker-compose up to start services
    - Run database migrations
    - Display success message with access URLs
    - _Requirements: 7.1_
  
  - [~] 15.5 Write Docker deployment documentation (DEPLOYMENT.md)
    - Document prerequisites (Docker, Docker Compose)
    - Document setup steps
    - Document how to start/stop services
    - Document how to view logs
    - Document troubleshooting common issues
    - _Requirements: 7.1_

- [ ] 16. Create Documentation
  - [~] 16.1 Create main README.md
    - Project overview and features
    - Architecture diagram
    - Quick start guide
    - Link to detailed documentation
    - Include TOS compliance disclaimer
    - _Requirements: 10.6_
  
  - [~] 16.2 Create ARCHITECTURE.md
    - Detailed system architecture
    - Component descriptions
    - Data flow diagrams
    - Technology stack rationale
    - _Requirements: 10.6_
  
  - [~] 16.3 Create API.md (if webhook endpoints exist)
    - Document webhook endpoints
    - Request/response formats
    - Authentication requirements
    - Example requests with curl
    - _Requirements: 4.1, 4.4_
  
  - [~] 16.4 Create SECURITY.md
    - Security best practices
    - Credential management
    - Rate limiting configuration
    - Data privacy considerations
    - Compliance with platform TOS
    - _Requirements: 10.1, 10.2, 10.3, 10.6, 10.7_
  
  - [~] 16.5 Create CONTRIBUTING.md
    - Code style guidelines
    - Testing requirements
    - Pull request process
    - _Requirements: 9.1_

- [ ] 17. Integration Testing
  - [~] 17.1 Write integration test for end-to-end scraping flow
    - Set up test environment with Docker Compose
    - Execute scraper against mock social media server
    - Verify data is scraped, analyzed, stored in database
    - Verify notifications are sent
    - Clean up test data
    - _Requirements: 1.1, 1.2, 2.1, 6.2, 6.3_
  
  - [~] 17.2 Write integration test for n8n workflows
    - Import workflows into test n8n instance
    - Trigger each workflow with test data
    - Verify workflow execution completes successfully
    - Verify data is stored correctly
    - _Requirements: 3.1, 4.1, 5.1_
  
  - [~] 17.3 Write integration test for database operations
    - Test with actual PostgreSQL instance
    - Verify schema creation from migrations
    - Test CRUD operations
    - Test data persistence across container restarts
    - Test backup and restore procedures
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 12.1, 12.5_
  
  - [~] 17.4 Write integration test for Docker Compose
    - Start all services with docker-compose up
    - Verify all containers are healthy
    - Verify inter-service connectivity
    - Verify volume persistence
    - Test graceful shutdown and restart
    - _Requirements: 7.1, 7.2, 7.3, 7.5, 7.7_

- [~] 18. Final Checkpoint and Validation
  - Ensure all tests pass (unit, property, integration)
  - Verify all documentation is complete and accurate
  - Test full deployment from scratch using setup script
  - Verify all environment variables are documented
  - Verify backup and restore procedures work
  - Ask the user if questions arise or if any adjustments are needed.

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end system behavior
- All sensitive data (credentials, API keys) must be managed via environment variables
- Docker deployment ensures consistency across development and production environments
- Comprehensive documentation enables easy onboarding and maintenance
