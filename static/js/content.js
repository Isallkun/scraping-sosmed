/**
 * Content Analysis Page JavaScript
 * 
 * Handles data loading and visualization for content pattern analysis.
 */

// Chart instances
let hashtagsChart = null;
let lengthDistributionChart = null;
let keywordsChart = null;

// Current filter state
let currentFilters = {
    start_date: null,
    end_date: null
};

/**
 * Load content data from API
 */
async function loadContentData() {
    try {
        const data = await dashboardUtils.fetchData('/api/content', currentFilters);
        updateContentSummary(data);
        updateHashtagsChart(data.hashtags);
        updatePostingHeatmap(data.posting_heatmap);
        updateLengthDistributionChart(data.length_distribution);
        updateKeywordsChart(data.keywords);
    } catch (error) {
        console.error('Failed to load content data:', error);
    }
}

/**
 * Update content summary cards
 */
function updateContentSummary(data) {
    document.getElementById('total-hashtags').textContent = 
        dashboardUtils.formatNumber(data.total_hashtags || 0);
    
    document.getElementById('avg-caption-length').textContent = 
        dashboardUtils.formatNumber(Math.round(data.avg_caption_length || 0));
    
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    document.getElementById('most-active-day').textContent = 
        days[data.most_active_day] || '-';
    
    const hour = data.most_active_hour;
    if (hour !== null && hour !== undefined) {
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        document.getElementById('most-active-hour').textContent = `${displayHour} ${ampm}`;
    } else {
        document.getElementById('most-active-hour').textContent = '-';
    }
}

/**
 * Update hashtags chart
 */
function updateHashtagsChart(hashtags) {
    const ctx = document.getElementById('hashtags-chart');
    if (!ctx) return;
    
    const colors = dashboardUtils.getChartColors();
    
    // Destroy existing chart
    if (hashtagsChart) {
        hashtagsChart.destroy();
    }
    
    // Prepare data - take top 20
    const topHashtags = (hashtags || []).slice(0, 20);
    const labels = topHashtags.map(item => '#' + item.tag);
    const values = topHashtags.map(item => item.count);
    
    if (labels.length === 0) {
        labels.push('No hashtags found');
        values.push(0);
    }
    
    // Create chart
    hashtagsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Frequency',
                data: values,
                backgroundColor: colors.primary + 'cc',
                borderColor: colors.primary,
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
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
                            return `Used ${context.parsed.x} times`;
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
                        color: colors.grid
                    },
                    beginAtZero: true
                },
                y: {
                    ticks: {
                        color: colors.text,
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Update posting heatmap
 */
function updatePostingHeatmap(heatmapData) {
    const container = document.getElementById('heatmap-container');
    if (!container) return;
    
    const isDark = document.documentElement.classList.contains('dark');
    
    // Days and hours
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const hours = Array.from({length: 24}, (_, i) => i);
    
    // Create 2D array for heatmap
    const heatmap = Array(7).fill(null).map(() => Array(24).fill(0));
    
    // Fill heatmap with data
    (heatmapData || []).forEach(item => {
        if (item.day >= 0 && item.day < 7 && item.hour >= 0 && item.hour < 24) {
            heatmap[item.day][item.hour] = item.count;
        }
    });
    
    // Find max value for color scaling
    const maxCount = Math.max(...heatmap.flat(), 1);
    
    // Generate HTML for heatmap
    let html = '<div class="inline-block min-w-full">';
    html += '<table class="border-collapse">';
    
    // Header row with hours
    html += '<tr><th class="p-2 text-xs text-gray-600 dark:text-gray-400"></th>';
    hours.forEach(hour => {
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        html += `<th class="p-1 text-xs text-gray-600 dark:text-gray-400">${displayHour}${ampm}</th>`;
    });
    html += '</tr>';
    
    // Data rows
    days.forEach((day, dayIndex) => {
        html += `<tr><td class="p-2 text-sm font-medium text-gray-700 dark:text-gray-300">${day}</td>`;
        hours.forEach(hour => {
            const count = heatmap[dayIndex][hour];
            const intensity = count / maxCount;
            
            // Color based on intensity
            let bgColor;
            if (isDark) {
                bgColor = `rgba(59, 130, 246, ${intensity * 0.8})`; // Blue in dark mode
            } else {
                bgColor = `rgba(59, 130, 246, ${intensity})`; // Blue in light mode
            }
            
            html += `<td class="p-2 border border-gray-200 dark:border-gray-700 text-center text-xs" 
                         style="background-color: ${bgColor}; min-width: 40px; height: 40px;"
                         title="${day} ${hour}:00 - ${count} posts">
                         ${count > 0 ? count : ''}
                     </td>`;
        });
        html += '</tr>';
    });
    
    html += '</table></div>';
    
    container.innerHTML = html;
}

/**
 * Update length distribution chart
 */
function updateLengthDistributionChart(distribution) {
    const ctx = document.getElementById('length-distribution-chart');
    if (!ctx) return;
    
    const colors = dashboardUtils.getChartColors();
    
    // Destroy existing chart
    if (lengthDistributionChart) {
        lengthDistributionChart.destroy();
    }
    
    // Prepare data
    const labels = (distribution || []).map(item => item.bin);
    const values = (distribution || []).map(item => item.count);
    
    if (labels.length === 0) {
        labels.push('No data');
        values.push(0);
    }
    
    // Create chart
    lengthDistributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Posts',
                data: values,
                backgroundColor: colors.success + 'cc',
                borderColor: colors.success,
                borderWidth: 1
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
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Caption Length (characters)',
                        color: colors.text
                    },
                    ticks: {
                        color: colors.text
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Number of Posts',
                        color: colors.text
                    },
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
 * Update keywords chart
 */
function updateKeywordsChart(keywords) {
    const ctx = document.getElementById('keywords-chart');
    if (!ctx) return;
    
    const colors = dashboardUtils.getChartColors();
    
    // Destroy existing chart
    if (keywordsChart) {
        keywordsChart.destroy();
    }
    
    // Prepare data - take top 15
    const topKeywords = (keywords || []).slice(0, 15);
    const labels = topKeywords.map(item => item.word);
    const values = topKeywords.map(item => item.count);
    
    if (labels.length === 0) {
        labels.push('No keywords found');
        values.push(0);
    }
    
    // Create chart
    keywordsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Frequency',
                data: values,
                backgroundColor: colors.warning + 'cc',
                borderColor: colors.warning,
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
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
                            return `Used ${context.parsed.x} times`;
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
                        color: colors.grid
                    },
                    beginAtZero: true
                },
                y: {
                    ticks: {
                        color: colors.text,
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        display: false
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
    
    loadContentData();
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
    loadContentData();
}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize date inputs
    initializeDateInputs();
    
    // Load initial data
    loadContentData();
    
    // Set up filter button
    const applyButton = document.getElementById('apply-filter');
    if (applyButton) {
        applyButton.addEventListener('click', applyFilter);
    }
    
    // Listen for theme changes
    window.addEventListener('themeChanged', handleThemeChange);
    
    console.log('Content page initialized');
});
