/**
 * Home Page JavaScript
 * 
 * Handles data loading and visualization for the dashboard overview page.
 */

// Chart instances
let postTypeChart = null;
let activityTimelineChart = null;

/**
 * Load summary data from API
 */
async function loadSummaryData() {
    try {
        const data = await dashboardUtils.fetchData('/api/summary');
        updateSummaryMetrics(data);
        updatePostTypeChart(data.post_type_distribution);
        updateActivityTimeline(data.activity_timeline);
        updateQuickStats(data);
    } catch (error) {
        console.error('Failed to load summary data:', error);
    }
}

/**
 * Update summary metric cards
 */
function updateSummaryMetrics(data) {
    // Total Posts
    document.getElementById('total-posts').textContent = 
        dashboardUtils.formatNumber(data.total_posts || 0);
    
    // Total Comments
    document.getElementById('total-comments').textContent = 
        dashboardUtils.formatNumber(data.total_comments || 0);
    
    // Average Sentiment
    const avgSentiment = data.avg_sentiment || 0;
    document.getElementById('avg-sentiment').textContent = avgSentiment.toFixed(3);
    
    // Sentiment Badge
    const sentimentBadge = document.getElementById('sentiment-badge');
    if (avgSentiment > 0.05) {
        sentimentBadge.innerHTML = '<span class="badge badge-success">Positive</span>';
    } else if (avgSentiment < -0.05) {
        sentimentBadge.innerHTML = '<span class="badge badge-danger">Negative</span>';
    } else {
        sentimentBadge.innerHTML = '<span class="badge badge-neutral">Neutral</span>';
    }
    
    // Last Execution
    if (data.last_execution) {
        const exec = data.last_execution;
        document.getElementById('last-execution-time').textContent =
            exec.timestamp ? dashboardUtils.formatDate(exec.timestamp, 'long') : 'No data';
        document.getElementById('posts-scraped').textContent =
            dashboardUtils.formatNumber(exec.posts_scraped || 0);

        const statusBadge = document.getElementById('execution-status');
        const status = exec.status || 'unknown';
        statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        statusBadge.className = `badge ${status === 'success' ? 'badge-success' : 'badge-warning'}`;
    } else {
        document.getElementById('last-execution-time').textContent = 'No data';
        document.getElementById('posts-scraped').textContent = '0';
        document.getElementById('execution-status').textContent = 'N/A';
    }
}

/**
 * Update post type distribution chart
 */
function updatePostTypeChart(distribution) {
    const ctx = document.getElementById('post-type-chart');
    if (!ctx) return;
    
    const colors = dashboardUtils.getChartColors();
    
    // Destroy existing chart
    if (postTypeChart) {
        postTypeChart.destroy();
    }
    
    // Prepare data
    const labels = Object.keys(distribution || {});
    const values = Object.values(distribution || {});
    
    if (labels.length === 0) {
        labels.push('No Data');
        values.push(1);
    }
    
    // Create chart
    postTypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
            datasets: [{
                data: values,
                backgroundColor: [
                    colors.primary,
                    colors.success,
                    colors.warning,
                    colors.danger
                ],
                borderWidth: 2,
                borderColor: colors.background
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: colors.text,
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update activity timeline chart
 */
function updateActivityTimeline(timeline) {
    const ctx = document.getElementById('activity-timeline-chart');
    if (!ctx) return;
    
    const colors = dashboardUtils.getChartColors();
    
    // Destroy existing chart
    if (activityTimelineChart) {
        activityTimelineChart.destroy();
    }
    
    // Prepare data
    const labels = (timeline || []).map(item => dashboardUtils.formatDate(item.date, 'short'));
    const posts = (timeline || []).map(item => item.posts || 0);
    const comments = (timeline || []).map(item => item.comments || 0);
    
    // Create chart
    activityTimelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Posts',
                    data: posts,
                    borderColor: colors.primary,
                    backgroundColor: colors.primary + '20',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Comments',
                    data: comments,
                    borderColor: colors.success,
                    backgroundColor: colors.success + '20',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: colors.text,
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: colors.background,
                    titleColor: colors.text,
                    bodyColor: colors.text,
                    borderColor: colors.grid,
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: colors.text
                    },
                    grid: {
                        color: colors.grid,
                        display: false
                    }
                },
                y: {
                    ticks: {
                        color: colors.text
                    },
                    grid: {
                        color: colors.grid
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Update quick stats
 */
function updateQuickStats(data) {
    // Average Likes
    document.getElementById('avg-likes').textContent = 
        dashboardUtils.formatCompactNumber(data.avg_likes || 0);
    
    // Average Comments
    document.getElementById('avg-comments').textContent = 
        dashboardUtils.formatCompactNumber(data.avg_comments || 0);
    
    // Engagement Rate
    document.getElementById('engagement-rate').textContent = 
        dashboardUtils.formatPercent(data.engagement_rate || 0);
    
    // Total Reach (followers * posts)
    document.getElementById('total-reach').textContent = 
        dashboardUtils.formatCompactNumber(data.total_reach || 0);
}

/**
 * Refresh all data
 */
function refreshData() {
    console.log('Refreshing home page data...');
    loadSummaryData();
}

/**
 * Update charts when theme changes
 */
function handleThemeChange() {
    if (postTypeChart) {
        updatePostTypeChart(postTypeChart.data.datasets[0].data);
    }
    if (activityTimelineChart) {
        const timeline = activityTimelineChart.data.labels.map((label, i) => ({
            date: label,
            posts: activityTimelineChart.data.datasets[0].data[i],
            comments: activityTimelineChart.data.datasets[1].data[i]
        }));
        updateActivityTimeline(timeline);
    }
}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {
    // Load initial data
    loadSummaryData();
    
    // Set up refresh button
    const refreshButton = document.getElementById('refresh-button');
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshData);
    }
    
    // Set up auto-refresh
    if (typeof AUTO_REFRESH_INTERVAL !== 'undefined') {
        dashboardUtils.initAutoRefresh(refreshData, AUTO_REFRESH_INTERVAL);
    }
    
    // Listen for theme changes
    window.addEventListener('themeChanged', handleThemeChange);
    
    console.log('Home page initialized');
});
