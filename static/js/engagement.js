/**
 * Engagement Metrics Page JavaScript
 * 
 * Handles data loading and visualization for engagement analysis.
 */

// Chart instances
let engagementTrendChart = null;
let postTypeChart = null;
let scatterChart = null;

// Current filter state
let currentFilters = {
    start_date: null,
    end_date: null
};

// Current sort option
let currentSort = 'engagement_rate';

/**
 * Load engagement data from API
 */
async function loadEngagementData() {
    try {
        const data = await dashboardUtils.fetchData('/api/engagement', currentFilters);
        updateEngagementSummary(data);
        updateEngagementTrendChart(data.trends);
        updatePostTypeChart(data.type_distribution);
        updateTopPostsTable(data.top_posts);
        updateScatterChart(data.scatter_data);
    } catch (error) {
        console.error('Failed to load engagement data:', error);
    }
}

/**
 * Update engagement summary cards
 */
function updateEngagementSummary(data) {
    document.getElementById('avg-engagement-rate').textContent = 
        dashboardUtils.formatPercent(data.avg_engagement_rate || 0);
    
    document.getElementById('total-likes').textContent = 
        dashboardUtils.formatCompactNumber(data.total_likes || 0);
    
    document.getElementById('total-comments').textContent = 
        dashboardUtils.formatCompactNumber(data.total_comments || 0);
    
    document.getElementById('best-post-rate').textContent = 
        dashboardUtils.formatPercent(data.best_post_rate || 0);
}

/**
 * Update engagement trend chart
 */
function updateEngagementTrendChart(trends) {
    const ctx = document.getElementById('engagement-trend-chart');
    if (!ctx) return;
    
    const colors = dashboardUtils.getChartColors();
    
    // Destroy existing chart
    if (engagementTrendChart) {
        engagementTrendChart.destroy();
    }
    
    // Prepare data
    const labels = (trends || []).map(item => dashboardUtils.formatDate(item.date, 'short'));
    const rates = (trends || []).map(item => item.engagement_rate || item.engagement || 0);
    
    // Create chart
    engagementTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Engagement Rate (%)',
                data: rates,
                borderColor: colors.primary,
                backgroundColor: colors.primary + '20',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
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
                    display: false
                },
                tooltip: {
                    backgroundColor: colors.background,
                    titleColor: colors.text,
                    bodyColor: colors.text,
                    borderColor: colors.grid,
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return `Engagement: ${context.parsed.y.toFixed(2)}%`;
                        }
                    }
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
                        color: colors.text,
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
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
 * Update post type chart
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
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${dashboardUtils.formatPercent(percentage)}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update top posts table
 */
function updateTopPostsTable(posts) {
    const tbody = document.getElementById('top-posts-table');
    if (!tbody) return;
    
    if (!posts || posts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center py-8 text-gray-500">No data available</td></tr>';
        return;
    }
    
    // Sort posts based on current sort option
    const sortedPosts = [...posts].sort((a, b) => {
        return (b[currentSort] || 0) - (a[currentSort] || 0);
    }).slice(0, 10);

    tbody.innerHTML = sortedPosts.map((post, index) => {
        const caption = post.content || post.caption || '';
        const truncatedCaption = caption.length > 60 ? caption.substring(0, 60) + '...' : caption;
        const mediaType = post.media_type || post.post_type || 'post';

        return `
            <tr>
                <td class="font-medium">${index + 1}</td>
                <td class="font-medium">${post.author || 'Unknown'}</td>
                <td class="max-w-xs truncate" title="${caption}">${truncatedCaption}</td>
                <td class="text-right">${dashboardUtils.formatNumber(post.likes || 0)}</td>
                <td class="text-right">${dashboardUtils.formatNumber(post.comments || 0)}</td>
                <td class="text-right font-medium text-primary-600 dark:text-primary-400">
                    ${dashboardUtils.formatNumber(post.engagement || post.engagement_rate || 0)}
                </td>
                <td>
                    <span class="badge ${mediaType === 'reel' ? 'badge-primary' : 'badge-neutral'}">
                        ${mediaType}
                    </span>
                </td>
                <td class="text-sm">${dashboardUtils.formatDate(post.timestamp, 'short')}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Update scatter chart
 */
function updateScatterChart(scatterData) {
    const ctx = document.getElementById('scatter-chart');
    if (!ctx) return;
    
    const colors = dashboardUtils.getChartColors();
    
    // Destroy existing chart
    if (scatterChart) {
        scatterChart.destroy();
    }
    
    // Prepare data
    const data = (scatterData || []).map(item => ({
        x: item.likes || 0,
        y: item.comments || 0
    }));
    
    // Create chart
    scatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Posts',
                data: data,
                backgroundColor: colors.primary + '80',
                borderColor: colors.primary,
                borderWidth: 1,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: colors.background,
                    titleColor: colors.text,
                    bodyColor: colors.text,
                    borderColor: colors.grid,
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return [
                                `Likes: ${dashboardUtils.formatNumber(context.parsed.x)}`,
                                `Comments: ${dashboardUtils.formatNumber(context.parsed.y)}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Likes',
                        color: colors.text
                    },
                    ticks: {
                        color: colors.text,
                        callback: function(value) {
                            return dashboardUtils.formatCompactNumber(value);
                        }
                    },
                    grid: {
                        color: colors.grid
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Comments',
                        color: colors.text
                    },
                    ticks: {
                        color: colors.text,
                        callback: function(value) {
                            return dashboardUtils.formatCompactNumber(value);
                        }
                    },
                    grid: {
                        color: colors.grid
                    }
                }
            }
        }
    });
}

/**
 * Apply date range filter
 */
function applyFilter() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    currentFilters.start_date = startDate || null;
    currentFilters.end_date = endDate || null;
    
    loadEngagementData();
}

/**
 * Handle sort change
 */
function handleSortChange() {
    const sortBy = document.getElementById('sort-by');
    if (sortBy) {
        currentSort = sortBy.value;
        loadEngagementData();
    }
}

/**
 * Initialize date inputs with default range (last 30 days)
 */
function initializeDateInputs() {
    const dateRange = dashboardUtils.getDateRange('month');
    document.getElementById('start-date').value = dateRange.start_date;
    document.getElementById('end-date').value = dateRange.end_date;
    
    currentFilters.start_date = dateRange.start_date;
    currentFilters.end_date = dateRange.end_date;
}

/**
 * Update charts when theme changes
 */
function handleThemeChange() {
    loadEngagementData();
}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize date inputs
    initializeDateInputs();
    
    // Load initial data
    loadEngagementData();
    
    // Set up filter button
    const applyButton = document.getElementById('apply-filter');
    if (applyButton) {
        applyButton.addEventListener('click', applyFilter);
    }
    
    // Set up sort dropdown
    const sortBy = document.getElementById('sort-by');
    if (sortBy) {
        sortBy.addEventListener('change', handleSortChange);
    }
    
    // Listen for theme changes
    window.addEventListener('themeChanged', handleThemeChange);
    
    console.log('Engagement page initialized');
});
