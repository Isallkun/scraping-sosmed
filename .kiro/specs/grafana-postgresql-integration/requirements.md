# Requirements Document

## Introduction

This document specifies the requirements for integrating Grafana with PostgreSQL to visualize Instagram scraping results. The system will enable users to import scraped data (posts, comments, sentiment analysis) from JSON/CSV files into a PostgreSQL database and visualize the data through pre-configured Grafana dashboards. The integration uses manual setup with local PostgreSQL and standalone Grafana on Windows, providing flexibility and direct control over the environment.

## Glossary

- **System**: The Grafana-PostgreSQL integration system including import scripts, database, and dashboards
- **Import_Script**: Python script that imports JSON/CSV data into PostgreSQL
- **Grafana**: Open-source analytics and visualization platform
- **PostgreSQL**: Relational database management system
- **Dashboard**: Grafana visualization interface displaying metrics and charts
- **Data_Source**: Grafana connection configuration to PostgreSQL
- **Sentiment_Data**: Analyzed sentiment scores and labels from VADER/TextBlob models
- **Engagement_Metrics**: Post interaction data including likes, comments, and shares
- **Provisioning_Directory**: Grafana directory containing configuration files for automatic dashboard and data source loading
- **Upsert**: Database operation that inserts or updates records based on conflict resolution

## Requirements

### Requirement 1: Data Import Functionality

**User Story:** As a data analyst, I want to import scraped Instagram data into PostgreSQL, so that I can analyze and visualize the data in Grafana.

#### Acceptance Criteria

1. WHEN the Import_Script is executed with a JSON file path, THE System SHALL parse the file and insert all posts into the posts table
2. WHEN the Import_Script encounters a post with an existing post_id, THE System SHALL update the existing record with new data (upsert logic)
3. WHEN the Import_Script processes sentiment data, THE System SHALL insert sentiment records linked to their corresponding posts via foreign key
4. WHEN the Import_Script processes a batch of records, THE System SHALL report progress every 10 records
5. WHEN the Import_Script encounters an error during import, THE System SHALL log the error and continue processing remaining records
6. WHEN the Import_Script completes execution, THE System SHALL display a summary showing total records processed, inserted, updated, and failed
7. WHEN the Import_Script is executed with a directory path, THE System SHALL process all JSON and CSV files in that directory
8. WHEN the Import_Script processes CSV files, THE System SHALL map CSV columns to database schema fields correctly
9. WHEN the Import_Script detects duplicate records within a single import batch, THE System SHALL skip the duplicates and log a warning

### Requirement 2: Incremental Import Support

**User Story:** As a data analyst, I want to import only new data without re-importing existing records, so that I can efficiently update my database with fresh scraping results.

#### Acceptance Criteria

1. WHEN the Import_Script is executed with incremental mode enabled, THE System SHALL check for existing post_id values before inserting
2. WHEN a post already exists in the database, THE System SHALL compare timestamps and update only if the new data is more recent
3. WHEN the Import_Script runs in incremental mode, THE System SHALL track and report the number of skipped records
4. WHEN the Import_Script processes comments data, THE System SHALL avoid inserting duplicate comments based on author and timestamp combination

### Requirement 3: Manual Environment Setup

**User Story:** As a developer, I want to set up Grafana and PostgreSQL manually on Windows localhost, so that I can use my existing local database and run Grafana without Docker containers.

#### Acceptance Criteria

1. WHEN the setup guide is followed, THE System SHALL connect to the existing local PostgreSQL instance at localhost:5432
2. WHEN Grafana is downloaded and extracted, THE System SHALL run as a standalone Windows executable or binary
3. WHEN Grafana starts, THE System SHALL be accessible at http://localhost:3000
4. WHEN Grafana is configured, THE System SHALL use local file paths for provisioning dashboards and data sources
5. WHEN the data source is configured, THE System SHALL connect to localhost PostgreSQL using local credentials
6. WHEN Grafana provisioning files are placed in the provisioning directory, THE System SHALL automatically load dashboards and data sources on startup
7. WHEN the setup is complete, THE System SHALL be ready for use in less than 15 minutes

### Requirement 4: Grafana Dashboard Provisioning

**User Story:** As a data analyst, I want pre-configured Grafana dashboards, so that I can immediately visualize my data without manual dashboard creation.

#### Acceptance Criteria

1. WHEN Grafana starts, THE System SHALL automatically load the Sentiment Overview Dashboard
2. WHEN Grafana starts, THE System SHALL automatically load the Engagement Metrics Dashboard
3. WHEN Grafana starts, THE System SHALL automatically load the Content Analysis Dashboard
4. WHEN a dashboard is loaded, THE System SHALL configure all panels to query the PostgreSQL data source
5. WHEN a dashboard is loaded, THE System SHALL set default time ranges to last 30 days
6. WHEN a user opens a dashboard, THE System SHALL display data refreshed within the last 5 seconds

### Requirement 5: Sentiment Visualization

**User Story:** As a data analyst, I want to visualize sentiment analysis results, so that I can understand the emotional tone of Instagram content over time.

#### Acceptance Criteria

1. WHEN the Sentiment Overview Dashboard is displayed, THE System SHALL show a pie chart with sentiment distribution (positive, neutral, negative)
2. WHEN the Sentiment Overview Dashboard is displayed, THE System SHALL show a line chart with sentiment trends over time
3. WHEN the Sentiment Overview Dashboard is displayed, THE System SHALL show a gauge displaying average sentiment score
4. WHEN sentiment data is updated in the database, THE System SHALL reflect changes in the dashboard within 5 seconds
5. WHEN the user selects a date range filter, THE System SHALL update all sentiment visualizations to match the selected range
6. WHEN the dashboard displays sentiment trends, THE System SHALL aggregate data by day for time periods longer than 7 days

### Requirement 6: Engagement Metrics Visualization

**User Story:** As a social media manager, I want to visualize engagement metrics, so that I can identify high-performing content and engagement patterns.

#### Acceptance Criteria

1. WHEN the Engagement Metrics Dashboard is displayed, THE System SHALL show total counts for posts and reels
2. WHEN the Engagement Metrics Dashboard is displayed, THE System SHALL show a table of top 10 posts ranked by total engagement (likes + comments + shares)
3. WHEN the Engagement Metrics Dashboard is displayed, THE System SHALL show a line chart of engagement rate over time
4. WHEN the Engagement Metrics Dashboard is displayed, THE System SHALL show a pie chart of post type distribution (posts vs reels)
5. WHEN the user hovers over a data point in the engagement chart, THE System SHALL display detailed metrics including likes, comments, and shares
6. WHEN the dashboard displays engagement trends, THE System SHALL calculate engagement rate as (likes + comments + shares) / total_posts

### Requirement 7: Content Analysis Visualization

**User Story:** As a content strategist, I want to analyze content patterns, so that I can optimize posting strategy and content themes.

#### Acceptance Criteria

1. WHEN the Content Analysis Dashboard is displayed, THE System SHALL show a bar chart of the top 20 most used hashtags
2. WHEN the Content Analysis Dashboard is displayed, THE System SHALL show a heatmap of posting frequency by day of week and hour
3. WHEN the Content Analysis Dashboard is displayed, THE System SHALL show average comments per post as a single stat panel
4. WHEN the Content Analysis Dashboard is displayed, THE System SHALL show a histogram of content length distribution
5. WHEN the user filters by date range, THE System SHALL update all content analysis visualizations accordingly
6. WHEN hashtags are displayed, THE System SHALL exclude hashtags that appear fewer than 3 times

### Requirement 8: SQL Query Library

**User Story:** As a developer, I want reusable SQL queries for common metrics, so that I can easily create custom dashboards or reports.

#### Acceptance Criteria

1. THE System SHALL provide a SQL query for sentiment distribution by label
2. THE System SHALL provide a SQL query for top posts by engagement with parameterized limit
3. THE System SHALL provide a SQL query for daily post counts with date range parameters
4. THE System SHALL provide a SQL query for sentiment trends over time with date range parameters
5. THE System SHALL provide a SQL query for hashtag frequency analysis
6. THE System SHALL provide a SQL query for engagement rate calculation
7. WHEN queries use date range parameters, THE System SHALL use parameterized queries to prevent SQL injection
8. WHEN queries are executed, THE System SHALL utilize existing database indexes for optimal performance

### Requirement 9: Documentation and Setup Guide

**User Story:** As a new user, I want clear setup instructions, so that I can get the system running in less than 15 minutes.

#### Acceptance Criteria

1. THE System SHALL provide a setup guide with step-by-step instructions for Windows
2. THE System SHALL provide documentation for running the Import_Script with examples
3. THE System SHALL provide documentation for customizing Grafana dashboards
4. THE System SHALL provide a troubleshooting guide for common issues
5. WHEN the documentation describes prerequisites, THE System SHALL list all required software with version numbers
6. WHEN the documentation describes the import process, THE System SHALL include example commands for both single file and batch imports
7. WHEN the documentation describes manual setup, THE System SHALL include instructions for downloading Grafana, configuring provisioning, and starting the service

### Requirement 10: Error Handling and Logging

**User Story:** As a system administrator, I want comprehensive error handling and logging, so that I can diagnose and resolve issues quickly.

#### Acceptance Criteria

1. WHEN the Import_Script encounters a database connection error, THE System SHALL retry the connection up to 3 times with exponential backoff
2. WHEN the Import_Script encounters invalid JSON data, THE System SHALL log the error with file name and line number
3. WHEN the Import_Script encounters a foreign key constraint violation, THE System SHALL log the error and skip the problematic record
4. WHEN Grafana fails to connect to PostgreSQL, THE System SHALL display a clear error message in the data source configuration
5. WHEN the Import_Script runs, THE System SHALL write logs to both console and a log file
6. WHEN an error occurs during import, THE System SHALL include the full error stack trace in the log file
7. WHEN the Import_Script completes, THE System SHALL log execution time and performance metrics

### Requirement 11: Data Validation

**User Story:** As a data analyst, I want data validation during import, so that I can ensure data quality and consistency in the database.

#### Acceptance Criteria

1. WHEN the Import_Script processes a post record, THE System SHALL validate that required fields (post_id, platform, author, content, timestamp) are present
2. WHEN the Import_Script processes a sentiment record, THE System SHALL validate that score values are between -1 and 1
3. WHEN the Import_Script processes a timestamp field, THE System SHALL validate that the timestamp is in a valid ISO 8601 format
4. WHEN the Import_Script encounters invalid data, THE System SHALL log the validation error and skip the record
5. WHEN the Import_Script processes hashtags, THE System SHALL normalize hashtag format by removing # prefix and converting to lowercase
6. WHEN the Import_Script processes engagement metrics, THE System SHALL validate that likes, comments, and shares are non-negative integers

### Requirement 12: Performance Optimization

**User Story:** As a data analyst, I want fast import and query performance, so that I can work efficiently with large datasets.

#### Acceptance Criteria

1. WHEN the Import_Script processes more than 100 records, THE System SHALL use batch insert operations
2. WHEN the Import_Script performs batch inserts, THE System SHALL commit transactions every 50 records
3. WHEN Grafana queries execute, THE System SHALL utilize database indexes on timestamp, platform, and post_id columns
4. WHEN the Import_Script processes large files, THE System SHALL stream data rather than loading entire files into memory
5. WHEN dashboard queries execute, THE System SHALL complete within 2 seconds for datasets up to 10,000 records
