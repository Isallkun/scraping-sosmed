# Requirements Document

## Introduction

This document specifies the requirements for a Flask-based web dashboard that visualizes Instagram scraping results stored in PostgreSQL. The dashboard provides an alternative to Grafana with greater customization flexibility, running as a lightweight localhost application on Windows. It reuses the existing database schema and import scripts from the grafana-postgresql-integration spec while providing interactive visualizations, filtering capabilities, and a responsive user interface.

## Glossary

- **Dashboard**: The Flask web application that displays visualizations and metrics
- **Flask_App**: The Python Flask web server application
- **Database_Module**: The existing PostgreSQL database connection and operations code in `database/` folder
- **Import_Script**: The Python script that imports JSON/CSV data into PostgreSQL
- **Visualization_Component**: A chart, graph, or table displaying data
- **API_Endpoint**: A RESTful HTTP endpoint that returns JSON data
- **Cache_Manager**: The Flask-Caching component that stores query results
- **Web_Interface**: The HTML/CSS/JavaScript frontend of the dashboard
- **Data_Explorer**: The searchable and filterable table view of posts
- **Sentiment_Score**: A numerical value representing sentiment polarity (-1 to 1)
- **Engagement_Rate**: The ratio of interactions (likes + comments) to followers
- **Post_Type**: Classification of content as either "post" or "reel"
- **Date_Range_Filter**: User-selected start and end dates for filtering data
- **Chart_Library**: The JavaScript library used for rendering visualizations (Chart.js or Plotly)

## Requirements

### Requirement 1: Flask Web Application Setup

**User Story:** As a developer, I want to set up a Flask web application, so that I can serve the dashboard on localhost.

#### Acceptance Criteria

1. THE Flask_App SHALL run on localhost port 5000
2. WHEN the Flask_App starts, THE Flask_App SHALL connect to the PostgreSQL database using Database_Module
3. THE Flask_App SHALL serve static files (CSS, JavaScript, images) from a static directory
4. THE Flask_App SHALL render HTML templates from a templates directory
5. WHEN the Flask_App encounters an error, THE Flask_App SHALL log the error and return an appropriate HTTP status code
6. THE Flask_App SHALL support configuration via environment variables for database connection parameters
7. THE Flask_App SHALL initialize the Cache_Manager on startup

### Requirement 2: Responsive Web Interface

**User Story:** As a user, I want a responsive web interface, so that I can view the dashboard on desktop, tablet, and mobile devices.

#### Acceptance Criteria

1. THE Web_Interface SHALL use Bootstrap or Tailwind CSS for responsive layout
2. WHEN viewed on mobile devices, THE Web_Interface SHALL display visualizations in a single-column layout
3. WHEN viewed on desktop devices, THE Web_Interface SHALL display visualizations in a multi-column grid layout
4. THE Web_Interface SHALL include a navigation menu that collapses on mobile devices
5. THE Web_Interface SHALL support both light and dark theme modes
6. WHEN a user switches themes, THE Web_Interface SHALL persist the theme preference in browser storage

### Requirement 3: Home/Overview Dashboard Page

**User Story:** As a user, I want to see an overview dashboard, so that I can quickly understand key metrics and recent activity.

#### Acceptance Criteria

1. THE Home_Page SHALL display total post count from the database
2. THE Home_Page SHALL display total comment count from the database
3. THE Home_Page SHALL display average sentiment score across all posts
4. THE Home_Page SHALL display the most recent scraping execution timestamp
5. THE Home_Page SHALL display a summary of posts by type (posts vs reels)
6. WHEN the page loads, THE Home_Page SHALL fetch data from API_Endpoint within 2 seconds
7. THE Home_Page SHALL include an auto-refresh toggle that updates data every 30 seconds when enabled

### Requirement 4: Sentiment Analysis Visualization

**User Story:** As a user, I want to visualize sentiment analysis results, so that I can understand the emotional tone of Instagram content.

#### Acceptance Criteria

1. THE Sentiment_Page SHALL display a pie chart showing distribution of positive, neutral, and negative sentiments
2. THE Sentiment_Page SHALL display a line chart showing sentiment trends over time
3. THE Sentiment_Page SHALL display sentiment gauge indicators for average sentiment score
4. WHEN a Date_Range_Filter is applied, THE Sentiment_Page SHALL update all visualizations to reflect the filtered date range
5. THE Sentiment_Page SHALL classify sentiments as positive (score > 0.05), neutral (-0.05 to 0.05), or negative (score < -0.05)
6. THE Sentiment_Page SHALL display the count and percentage for each sentiment category

### Requirement 5: Engagement Metrics Visualization

**User Story:** As a user, I want to visualize engagement metrics, so that I can identify high-performing content.

#### Acceptance Criteria

1. THE Engagement_Page SHALL display a table of top 10 posts sorted by engagement rate
2. THE Engagement_Page SHALL display a time series chart showing engagement rate trends over time
3. THE Engagement_Page SHALL display a pie chart showing distribution by Post_Type
4. WHEN a user clicks on a post in the top posts table, THE Engagement_Page SHALL display detailed post information
5. THE Engagement_Page SHALL calculate Engagement_Rate as (likes + comments) / followers for each post
6. THE Engagement_Page SHALL allow sorting the top posts table by likes, comments, or engagement rate

### Requirement 6: Content Analysis Visualization

**User Story:** As a user, I want to analyze content patterns, so that I can understand posting behavior and content characteristics.

#### Acceptance Criteria

1. THE Content_Page SHALL display a word cloud or bar chart of top 20 hashtags by frequency
2. THE Content_Page SHALL display a heatmap showing posting patterns by day of week and hour of day
3. THE Content_Page SHALL display a histogram showing distribution of content length (character count)
4. WHEN a Date_Range_Filter is applied, THE Content_Page SHALL update all visualizations accordingly
5. THE Content_Page SHALL extract hashtags from post captions using regex pattern matching
6. THE Content_Page SHALL group posting times into hourly bins for the heatmap

### Requirement 7: Data Explorer with Search and Filtering

**User Story:** As a user, I want to search and filter posts, so that I can find specific content and export filtered results.

#### Acceptance Criteria

1. THE Data_Explorer SHALL display a paginated table of all posts with columns for author, caption, likes, comments, sentiment, and timestamp
2. WHEN a user enters a search term, THE Data_Explorer SHALL filter posts where the caption or author contains the search term
3. WHEN a user applies filters, THE Data_Explorer SHALL update the table to show only matching posts
4. THE Data_Explorer SHALL support filtering by Date_Range_Filter, Post_Type, and sentiment category
5. WHEN a user clicks the export button, THE Data_Explorer SHALL generate a CSV file containing the filtered results
6. THE Data_Explorer SHALL display 25 posts per page with pagination controls
7. THE Data_Explorer SHALL allow sorting by any column in ascending or descending order

### Requirement 8: RESTful API Endpoints

**User Story:** As a developer, I want RESTful API endpoints, so that I can access dashboard data programmatically and support future integrations.

#### Acceptance Criteria

1. THE Flask_App SHALL provide an API_Endpoint at `/api/summary` that returns overall statistics in JSON format
2. THE Flask_App SHALL provide an API_Endpoint at `/api/sentiment` that returns sentiment distribution and trends in JSON format
3. THE Flask_App SHALL provide an API_Endpoint at `/api/engagement` that returns engagement metrics in JSON format
4. THE Flask_App SHALL provide an API_Endpoint at `/api/content` that returns content analysis data in JSON format
5. THE Flask_App SHALL provide an API_Endpoint at `/api/posts` that returns paginated post data in JSON format
6. WHEN an API_Endpoint receives date range parameters, THE API_Endpoint SHALL filter results accordingly
7. THE Flask_App SHALL support CORS headers on all API endpoints for cross-origin requests
8. WHEN an API_Endpoint receives invalid parameters, THE API_Endpoint SHALL return a 400 status code with an error message

### Requirement 9: Data Import Integration

**User Story:** As a user, I want to import Instagram data into the database, so that the dashboard displays current information.

#### Acceptance Criteria

1. THE Import_Script SHALL read JSON and CSV files from the output directory structure
2. WHEN the Import_Script runs, THE Import_Script SHALL insert new posts into the database using Database_Module operations
3. WHEN the Import_Script encounters duplicate posts, THE Import_Script SHALL update existing records instead of creating duplicates
4. THE Import_Script SHALL support batch import of multiple files in a single execution
5. THE Import_Script SHALL provide a CLI interface with arguments for file paths and import options
6. WHEN the Import_Script completes, THE Import_Script SHALL log the number of records inserted and updated
7. THE Import_Script SHALL validate data before insertion and skip invalid records with a warning

### Requirement 10: Query Result Caching

**User Story:** As a user, I want fast page load times, so that I can efficiently navigate the dashboard.

#### Acceptance Criteria

1. THE Cache_Manager SHALL cache results from database queries for API endpoints
2. WHEN an API_Endpoint is called, THE Cache_Manager SHALL return cached results if available and not expired
3. THE Cache_Manager SHALL expire cached results after 5 minutes
4. WHEN new data is imported, THE Cache_Manager SHALL invalidate all cached results
5. THE Flask_App SHALL configure cache timeout values via environment variables
6. THE Cache_Manager SHALL use in-memory caching for development and Redis for production

### Requirement 11: Interactive Chart Features

**User Story:** As a user, I want interactive charts, so that I can explore data dynamically and drill down into details.

#### Acceptance Criteria

1. WHEN a user hovers over a chart element, THE Visualization_Component SHALL display a tooltip with detailed information
2. WHEN a user clicks on a chart element, THE Visualization_Component SHALL filter or drill down to related data
3. THE Visualization_Component SHALL support zooming and panning on time series charts
4. THE Visualization_Component SHALL support toggling data series visibility on multi-series charts
5. THE Visualization_Component SHALL load data asynchronously to prevent blocking page rendering
6. WHEN chart data is loading, THE Visualization_Component SHALL display a loading indicator

### Requirement 12: Performance Optimization

**User Story:** As a user, I want the dashboard to load quickly, so that I can access information without delays.

#### Acceptance Criteria

1. WHEN a user navigates to any dashboard page, THE Web_Interface SHALL complete initial page load within 2 seconds
2. THE Flask_App SHALL use database query optimization with appropriate indexes
3. THE Flask_App SHALL implement lazy loading for large datasets in the Data_Explorer
4. THE Web_Interface SHALL load Chart_Library scripts asynchronously
5. THE Flask_App SHALL compress HTTP responses using gzip compression
6. THE Database_Module SHALL use connection pooling to minimize connection overhead

### Requirement 13: Configuration Management

**User Story:** As a developer, I want configurable settings, so that I can customize the dashboard for different environments.

#### Acceptance Criteria

1. THE Flask_App SHALL read database connection parameters from environment variables (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
2. THE Flask_App SHALL read the server port from an environment variable with default value 5000
3. THE Flask_App SHALL read cache timeout values from environment variables with default value 300 seconds
4. THE Flask_App SHALL read auto-refresh interval from an environment variable with default value 30 seconds
5. THE Flask_App SHALL support a DEBUG environment variable to enable/disable debug mode
6. WHEN environment variables are missing, THE Flask_App SHALL use sensible default values and log a warning

### Requirement 14: Error Handling and Logging

**User Story:** As a developer, I want comprehensive error handling, so that I can diagnose and fix issues quickly.

#### Acceptance Criteria

1. WHEN a database connection fails, THE Flask_App SHALL log the error and display a user-friendly error page
2. WHEN an API_Endpoint encounters an error, THE API_Endpoint SHALL return a JSON error response with appropriate HTTP status code
3. THE Flask_App SHALL log all HTTP requests with timestamp, method, path, and response status
4. THE Flask_App SHALL log all database queries in debug mode
5. WHEN an unhandled exception occurs, THE Flask_App SHALL log the full stack trace and return a 500 error page
6. THE Flask_App SHALL write logs to both console and a rotating log file

### Requirement 15: Database Schema Compatibility

**User Story:** As a developer, I want to use the existing database schema, so that I can share data with the Grafana integration.

#### Acceptance Criteria

1. THE Flask_App SHALL query the `posts` table as defined in `database/migrations/001_initial_schema.sql`
2. THE Flask_App SHALL query the `comments` table as defined in the database schema
3. THE Flask_App SHALL query the `sentiment_analysis` table as defined in the database schema
4. THE Flask_App SHALL query the `scraping_executions` table as defined in the database schema
5. THE Flask_App SHALL use the Database_Module functions from `database/db_operations.py` for all database operations
6. THE Flask_App SHALL NOT modify the existing database schema
