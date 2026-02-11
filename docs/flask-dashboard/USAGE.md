# Usage Guide

This guide explains how to use the Flask Analytics Dashboard features to analyze Instagram data.

## Table of Contents

- [Dashboard Overview](#dashboard-overview)
- [Navigation](#navigation)
- [Overview Page](#overview-page)
- [Sentiment Analysis](#sentiment-analysis)
- [Engagement Metrics](#engagement-metrics)
- [Content Analysis](#content-analysis)
- [Data Explorer](#data-explorer)
- [Data Import](#data-import)
- [Theme Customization](#theme-customization)
- [Tips and Best Practices](#tips-and-best-practices)

## Dashboard Overview

The Flask Analytics Dashboard provides five main pages for analyzing Instagram data:

1. **Overview** - Summary statistics and key metrics
2. **Sentiment** - Sentiment analysis visualizations
3. **Engagement** - Engagement metrics and top posts
4. **Content** - Content analysis (hashtags, posting patterns)
5. **Explorer** - Searchable data table with filters

## Navigation

### Desktop Navigation

The navigation menu is located at the top of the page with icons and labels:

- 🏠 **Overview** - Home page with summary statistics
- 😊 **Sentiment** - Sentiment analysis page
- 📈 **Engagement** - Engagement metrics page
- 📄 **Content** - Content analysis page
- 📊 **Explorer** - Data explorer page

### Mobile Navigation

On mobile devices, tap the menu icon (☰) in the top-right corner to access the navigation menu.

### Theme Toggle

Click the theme icon (☀️/🌙) in the top-right corner to switch between light and dark modes. Your preference is saved automatically.

## Overview Page

The Overview page displays key metrics and summary statistics.

### Summary Cards

Four main metrics are displayed:

1. **Total Posts** - Total number of posts in the database
2. **Total Comments** - Total number of comments across all posts
3. **Average Sentiment** - Average sentiment score (-1 to 1)
4. **Last Scraping** - Timestamp of the most recent data import

### Post Type Distribution

A pie chart showing the distribution of posts vs. reels.

### Auto-Refresh

Toggle the auto-refresh switch to automatically update data every 30 seconds (configurable).

## Sentiment Analysis

The Sentiment Analysis page provides insights into the emotional tone of Instagram content.

### Features

#### Sentiment Distribution (Pie Chart)

Shows the breakdown of posts by sentiment:
- **Positive** - Sentiment score > 0.05 (green)
- **Neutral** - Sentiment score between -0.05 and 0.05 (yellow)
- **Negative** - Sentiment score < -0.05 (red)

Hover over segments to see exact counts and percentages.

#### Sentiment Trends (Line Chart)

Displays sentiment scores over time:
- X-axis: Date
- Y-axis: Average sentiment score
- Hover over points to see exact values

#### Sentiment Gauge

A gauge indicator showing the overall average sentiment score:
- Green zone: Positive sentiment
- Yellow zone: Neutral sentiment
- Red zone: Negative sentiment

### Date Range Filtering

Use the date range picker to filter sentiment data:

1. Click the "From Date" field and select a start date
2. Click the "To Date" field and select an end date
3. Click "Apply Filter" to update the visualizations

**Tip**: Leave dates empty to view all data.

### Interpreting Sentiment Scores

- **Score > 0.05**: Positive sentiment (happy, excited, satisfied)
- **Score -0.05 to 0.05**: Neutral sentiment (informational, factual)
- **Score < -0.05**: Negative sentiment (angry, sad, disappointed)

## Engagement Metrics

The Engagement Metrics page helps identify high-performing content.

### Features

#### Top Posts Table

Displays the top 10 posts sorted by engagement rate:

- **Author** - Post author username
- **Caption** - Post caption (truncated)
- **Likes** - Number of likes
- **Comments** - Number of comments
- **Engagement Rate** - (Likes + Comments) / Followers × 100

**Sorting**: Click column headers to sort by different metrics.

**Details**: Click on a post row to view full details (if implemented).

#### Engagement Trends (Line Chart)

Shows engagement rate trends over time:
- X-axis: Date
- Y-axis: Average engagement rate
- Hover over points to see exact values

#### Post Type Distribution (Pie Chart)

Compares engagement between posts and reels.

### Date Range Filtering

Use the date range picker to analyze engagement for specific time periods.

### Understanding Engagement Rate

Engagement rate is calculated as:
```
Engagement Rate = (Likes + Comments) / Followers × 100
```

**Example**: A post with 100 likes, 20 comments, and 1000 followers has an engagement rate of 12%.

**Benchmarks**:
- **< 1%**: Low engagement
- **1-3%**: Average engagement
- **3-6%**: Good engagement
- **> 6%**: Excellent engagement

## Content Analysis

The Content Analysis page reveals patterns in posting behavior and content characteristics.

### Features

#### Top Hashtags (Bar Chart)

Displays the 20 most frequently used hashtags:
- X-axis: Hashtag count
- Y-axis: Hashtag name
- Hover over bars to see exact counts

**Use Case**: Identify trending topics and popular hashtags.

#### Posting Heatmap

Shows when posts are most frequently published:
- X-axis: Hour of day (0-23)
- Y-axis: Day of week (Sunday-Saturday)
- Color intensity: Number of posts

**Use Case**: Identify optimal posting times.

#### Content Length Distribution (Histogram)

Shows the distribution of post caption lengths:
- X-axis: Character count bins
- Y-axis: Number of posts

**Use Case**: Understand typical content length patterns.

### Date Range Filtering

Filter content analysis by date range to see how patterns change over time.

### Insights

- **Peak Posting Times**: Darker cells in the heatmap indicate popular posting times
- **Hashtag Strategy**: Top hashtags reveal content themes and topics
- **Content Length**: Optimal caption length for your audience

## Data Explorer

The Data Explorer provides a searchable, filterable table of all posts.

### Features

#### Search

Enter keywords in the search box to find posts:
- Searches in both caption and author fields
- Case-insensitive search
- Partial matches supported

**Example**: Search for "coffee" to find all posts mentioning coffee.

#### Filters

Apply multiple filters simultaneously:

1. **Date Range** - Filter by post date
2. **Post Type** - Filter by post or reel
3. **Sentiment** - Filter by positive, neutral, or negative sentiment

**Steps**:
1. Set filter values
2. Click "Apply Filters"
3. Click "Clear" to reset filters

#### Sorting

Click column headers to sort the table:
- **Author** - Alphabetical order
- **Likes** - Numerical order
- **Comments** - Numerical order
- **Sentiment** - Sentiment score order
- **Date** - Chronological order

Click again to reverse sort order (ascending/descending).

#### Pagination

Navigate through results:
- **First/Last** - Jump to first or last page
- **Previous/Next** - Move one page at a time
- **Page Numbers** - Click specific page numbers
- **Per Page** - Select 10, 25, 50, or 100 results per page

#### Export to CSV

Export filtered results to CSV:

1. Apply desired filters
2. Click "Export CSV" button
3. File downloads automatically

**Use Case**: Export data for further analysis in Excel or other tools.

### Example Workflows

#### Find High-Engagement Posts

1. Sort by "Likes" (descending)
2. Review top posts
3. Analyze common characteristics

#### Analyze Negative Sentiment

1. Filter by "Negative" sentiment
2. Review post captions
3. Identify common themes or issues

#### Export Monthly Data

1. Set date range to specific month
2. Apply filter
3. Click "Export CSV"

## Data Import

Import Instagram data into the dashboard using the import script.

### Import JSON Files

```bash
# Import all JSON files from a directory
python scripts/import_data.py --input output/instagram/raw/ --type json

# Import a single JSON file
python scripts/import_data.py --file output/instagram/raw/posts_20260209.json
```

### Import CSV Files

```bash
# Import all CSV files from a directory
python scripts/import_data.py --input output/instagram/sentiment/ --type csv

# Import a single CSV file
python scripts/import_data.py --file output/instagram/sentiment/posts_20260209.csv
```

### Batch Import

```bash
# Import all files recursively
python scripts/import_data.py --input output/instagram/ --type json --recursive --verbose
```

### Import Process

1. **Validation** - Script validates required fields (post_id, author, timestamp)
2. **Upsert** - Existing posts are updated, new posts are inserted
3. **Sentiment** - Sentiment data is imported if available
4. **Cache Invalidation** - Dashboard cache is cleared
5. **Summary** - Import summary is displayed

### Import Summary

After import, you'll see:
```
IMPORT SUMMARY
Total records imported: 150
Total records skipped:  5
```

**Skipped Records**: Records with missing required fields or invalid data.

### Troubleshooting Import

**Issue**: Records are skipped

**Solution**: Check the log messages for validation errors. Common issues:
- Missing required fields (post_id, author, timestamp)
- Invalid timestamp format
- Corrupted JSON/CSV file

## Theme Customization

### Switching Themes

Click the theme toggle button (☀️/🌙) in the top-right corner to switch between:
- **Light Mode** - White background, dark text
- **Dark Mode** - Dark background, light text

Your preference is saved in browser storage and persists across sessions.

### Theme Features

- **Automatic Chart Colors** - Charts adapt to the selected theme
- **Smooth Transitions** - Theme changes animate smoothly
- **Accessibility** - Both themes meet WCAG contrast requirements

## Tips and Best Practices

### Performance Tips

1. **Use Date Filters** - Filter data to specific date ranges for faster loading
2. **Limit Results** - Use pagination to view manageable chunks of data
3. **Cache Awareness** - Data is cached for 5 minutes; refresh if needed
4. **Export Large Datasets** - Use CSV export for large datasets instead of viewing in browser

### Analysis Tips

1. **Compare Time Periods** - Use date filters to compare different time periods
2. **Identify Patterns** - Look for patterns in the posting heatmap
3. **Track Trends** - Monitor sentiment and engagement trends over time
4. **Analyze Top Content** - Study top-performing posts to understand what works

### Data Quality Tips

1. **Regular Imports** - Import data regularly to keep dashboard current
2. **Validate Data** - Check import logs for skipped records
3. **Clean Data** - Ensure source data has required fields
4. **Monitor Sentiment** - Review sentiment analysis for accuracy

### Workflow Examples

#### Weekly Performance Review

1. Set date range to past 7 days
2. Review Overview page for summary metrics
3. Check Engagement page for top posts
4. Analyze Sentiment page for audience mood
5. Export data for reporting

#### Content Strategy Planning

1. Review Content page for top hashtags
2. Check posting heatmap for optimal times
3. Analyze engagement trends
4. Plan content calendar based on insights

#### Issue Investigation

1. Filter by negative sentiment
2. Review post captions in Data Explorer
3. Identify common themes
4. Export data for detailed analysis

## Keyboard Shortcuts

- **Ctrl/Cmd + K** - Focus search box (Data Explorer)
- **Ctrl/Cmd + R** - Refresh page
- **Esc** - Close modals or clear search

## Mobile Usage

The dashboard is fully responsive and works on mobile devices:

- **Navigation** - Tap menu icon to access pages
- **Charts** - Tap and hold to view tooltips
- **Tables** - Swipe horizontally to scroll
- **Filters** - Tap to expand filter controls

## Next Steps

- Review [API Documentation](API.md) for programmatic access
- Check [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues
- Explore advanced features and customization options

## Getting Help

If you need assistance:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review application logs in `logs/flask_dashboard.log`
3. Consult the [API Documentation](API.md) for technical details
