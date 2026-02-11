/**
 * Sentiment Analysis Page JavaScript
 * 
 * Handles data loading and visualization for sentiment analysis.
 */

// Chart instances
let sentimentPieChart = null;
let sentimentTrendChart = null;
let sentimentByTypeChart = null;

// Current filter state
let currentFilters = {
    start_date: null,
    end_date: null
};

/**
 * Load sentiment data from API
 */
async function loadSentimentData() {
    try {
        const data = await dashboardUtils.fetchData('/api/sentiment', currentFilters);
        updateSentimentSummary(data.distribution);
        updateSentimentGauge(data.gauge);
        updateSentimentPieChart(data.distribution);
        updateSentimentTrendChart(data.trends);
        updateSentimentByTypeChart(data.by_type);
    } catch (error) {
        console.error('Failed to load sentiment data:', error);
    }
}

/**
 * Update sentiment summary cards
 */
function updateSentimentSummary(distribution) {
    const positive = distribution.positive || 0;
    const neutral = distribution.neutral || 0;
    const negative = distribution.negative || 0;
    const total = positive + neutral + negative || 1; // Avoid division by zero
    
    // Update counts
    document.getElementById('positive-count').textContent = dashboardUtils.formatNumber(positive);
    document.getElementById('neutral-count').textContent = dashboardUtils.formatNumber(neutral);
    document.getElementById('negative-count').textContent = dashboardUtils.formatNumber(negative);
    
    // Update percentages
    const positivePercent = (positive / total * 100).toFixed(1);
    const neutralPercent = (neutral / total * 100).toFixed(1);
    const negativePercent = (negative / total * 100).toFixed(1);
    
    document.getElementById('positive-percent').textContent = `${positivePercent}% of total`;
    document.getElementById('neutral-percent').textContent = `${neutralPercent}% of total`;
    document.getElementById('negative-percent').textContent = `${negativePercent}% of total`;
    
    // Update progress bars
    document.getElementById('positive-progress').style.width = `${positivePercent}%`;
    document.getElementById('neutral-progress').style.width = `${neutralPercent}%`;
    document.getElementById('negative-progress').style.width = `${negativePercent}%`;
}

/**
 * Update sentiment gauge
 */
function updateSentimentGauge(gaugeValue) {
    const score = gaugeValue || 0;
    
    // Update gauge value
    document.getElementById('gauge-value').textContent = score.toFixed(3);
    
    // Update gauge label and color
    const gaugeLabel = document.getElementById('gauge-label');
    const gaugeValueEl = document.getElementById('gauge-value');
    
    if (score > 0.05) {
        gaugeLabel.innerHTML = '<span class="badge badge-success text-lg">Positive Sentiment</span>';
        gaugeValueEl.className = 'text-6xl font-bold text-green-600 dark:text-green-400';
    } else if (score < -0.05) {
        gaugeLabel.innerHTML = '<span class="badge badge-danger text-lg">Negative Sentiment</span>';
        gaugeValueEl.className = 'text-6xl font-bold text-red-600 dark:text-red-400';
    } else {
        gaugeLabel.innerHTML = '<span class="badge badge-neutral text-lg">Neutral Sentiment</span>';
        gaugeValueEl.className = 'text-6xl font-bold text-gray-600 dark:text-gray-400';
    }
    
    // Update gauge indicator position (-1 to 1 mapped to 0% to 100%)
    const position = ((score + 1) / 2) * 100;
    document.getElementById('gauge-indicator').style.left = `${position}%`;
}

/**
 * Update sentiment pie chart
 */
function updateSentimentPieChart(distribution) {
    const ctx = document.getElementById('sentiment-pie-chart');
    if (!ctx) return;
    
    const colors = dashboardUtils.getChartColors();
    
    // Destroy existing chart
    if (sentimentPieChart) {
        sentimentPieChart.destroy();
    }
    
    // Prepare data
    const positive = distribution.positive || 0;
    const neutral = distribution.neutral || 0;
    const negative = distribution.negative || 0;
    
    // Create chart
    sentimentPieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                data: [positive, neutral, negative],
                backgroundColor: [
                    colors.success,
                    '#9ca3af',
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
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update sentiment trend chart
 */
function updateSentimentTrendChart(trends) {
    const ctx = document.getElementById('sentiment-trend-chart');
    if (!ctx) return;
    
    const colors = dashboardUtils.getChartColors();
    
    // Destroy existing chart
    if (sentimentTrendChart) {
        sentimentTrendChart.destroy();
    }
    
    // Prepare data
    const labels = (trends || []).map(item => dashboardUtils.formatDate(item.date, 'short'));
    const scores = (trends || []).map(item => item.score || 0);
    
    // Create chart
    sentimentTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sentiment Score',
                data: scores,
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
                            return `Score: ${context.parsed.y.toFixed(3)}`;
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
                            return value.toFixed(2);
                        }
                    },
                    grid: {
                        color: colors.grid
                    },
                    min: -1,
                    max: 1
                }
            }
        }
    });
}

/**
 * Update sentiment by post type chart
 */
function updateSentimentByTypeChart(byType) {
    const ctx = document.getElementById('sentiment-by-type-chart');
    if (!ctx) return;
    
    const colors = dashboardUtils.getChartColors();
    
    // Destroy existing chart
    if (sentimentByTypeChart) {
        sentimentByTypeChart.destroy();
    }
    
    // Prepare data
    const types = Object.keys(byType || {});
    const positiveData = types.map(type => byType[type]?.positive || 0);
    const neutralData = types.map(type => byType[type]?.neutral || 0);
    const negativeData = types.map(type => byType[type]?.negative || 0);
    
    // Create chart
    sentimentByTypeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: types.map(t => t.charAt(0).toUpperCase() + t.slice(1)),
            datasets: [
                {
                    label: 'Positive',
                    data: positiveData,
                    backgroundColor: colors.success + 'cc'
                },
                {
                    label: 'Neutral',
                    data: neutralData,
                    backgroundColor: '#9ca3af' + 'cc'
                },
                {
                    label: 'Negative',
                    data: negativeData,
                    backgroundColor: colors.danger + 'cc'
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
                    stacked: true,
                    ticks: {
                        color: colors.text
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    stacked: true,
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
 * Apply date range filter
 */
function applyFilter() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    currentFilters.start_date = startDate || null;
    currentFilters.end_date = endDate || null;
    
    loadSentimentData();
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
    loadSentimentData();
}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize date inputs
    initializeDateInputs();
    
    // Load initial data
    loadSentimentData();
    
    // Set up filter button
    const applyButton = document.getElementById('apply-filter');
    if (applyButton) {
        applyButton.addEventListener('click', applyFilter);
    }
    
    // Listen for theme changes
    window.addEventListener('themeChanged', handleThemeChange);
    
    console.log('Sentiment page initialized');
});
