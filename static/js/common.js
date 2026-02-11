/**
 * Common JavaScript utilities for Flask Analytics Dashboard
 * 
 * This file contains shared functions used across all pages:
 * - Theme management (dark/light mode)
 * - AJAX helpers
 * - Date formatting
 * - Auto-refresh functionality
 * - Mobile menu toggle
 */

// ===== Theme Management =====

/**
 * Initialize theme toggle functionality
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Apply saved theme on page load
    applyTheme();
}

/**
 * Toggle between light and dark theme
 */
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.classList.contains('dark') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    if (newTheme === 'dark') {
        html.classList.add('dark');
    } else {
        html.classList.remove('dark');
    }
    
    // Save preference to localStorage
    localStorage.setItem('theme', newTheme);
    
    // Dispatch custom event for charts to update
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
}

/**
 * Apply saved theme from localStorage
 */
function applyTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const html = document.documentElement;
    
    if (savedTheme === 'dark') {
        html.classList.add('dark');
    } else {
        html.classList.remove('dark');
    }
}

// ===== Mobile Menu Toggle =====

/**
 * Initialize mobile menu toggle
 */
function initMobileMenu() {
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }
}

// ===== AJAX Helpers =====

/**
 * Fetch data from API endpoint with error handling
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} - Parsed JSON response
 */
async function fetchData(url, params = {}) {
    try {
        // Build query string from params
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        
        const response = await fetch(fullUrl);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        showError(`Failed to load data: ${error.message}`);
        throw error;
    }
}

/**
 * Post data to API endpoint
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} data - Data to send
 * @returns {Promise<Object>} - Parsed JSON response
 */
async function postData(url, data = {}) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const responseData = await response.json();
        return responseData;
    } catch (error) {
        console.error('Error posting data:', error);
        showError(`Failed to send data: ${error.message}`);
        throw error;
    }
}

// ===== Date Formatting =====

/**
 * Format date to readable string
 * 
 * @param {string|Date} date - Date to format
 * @param {string} format - Format type ('short', 'long', 'time')
 * @returns {string} - Formatted date string
 */
function formatDate(date, format = 'short') {
    const d = new Date(date);
    
    if (isNaN(d.getTime())) {
        return 'Invalid Date';
    }
    
    const options = {
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        long: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' },
        time: { hour: '2-digit', minute: '2-digit', second: '2-digit' }
    };
    
    return d.toLocaleDateString('en-US', options[format] || options.short);
}

/**
 * Format date for input fields (YYYY-MM-DD)
 * 
 * @param {string|Date} date - Date to format
 * @returns {string} - Formatted date string
 */
function formatDateForInput(date) {
    const d = new Date(date);
    
    if (isNaN(d.getTime())) {
        return '';
    }
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
}

/**
 * Get date range for common periods
 * 
 * @param {string} period - Period type ('today', 'week', 'month', 'year')
 * @returns {Object} - Object with start_date and end_date
 */
function getDateRange(period) {
    const end = new Date();
    const start = new Date();
    
    switch (period) {
        case 'today':
            start.setHours(0, 0, 0, 0);
            break;
        case 'week':
            start.setDate(start.getDate() - 7);
            break;
        case 'month':
            start.setMonth(start.getMonth() - 1);
            break;
        case 'year':
            start.setFullYear(start.getFullYear() - 1);
            break;
        default:
            start.setMonth(start.getMonth() - 1); // Default to last month
    }
    
    return {
        start_date: formatDateForInput(start),
        end_date: formatDateForInput(end)
    };
}

// ===== Number Formatting =====

/**
 * Format number with thousands separator
 * 
 * @param {number} num - Number to format
 * @returns {string} - Formatted number string
 */
function formatNumber(num) {
    if (num === null || num === undefined) {
        return '0';
    }
    return num.toLocaleString('en-US');
}

/**
 * Format number as percentage
 * 
 * @param {number} num - Number to format (0-100)
 * @param {number} decimals - Number of decimal places
 * @returns {string} - Formatted percentage string
 */
function formatPercent(num, decimals = 1) {
    if (num === null || num === undefined) {
        return '0%';
    }
    return `${num.toFixed(decimals)}%`;
}

/**
 * Format large numbers with K, M, B suffixes
 * 
 * @param {number} num - Number to format
 * @returns {string} - Formatted number string
 */
function formatCompactNumber(num) {
    if (num === null || num === undefined) {
        return '0';
    }
    
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1) + 'B';
    }
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// ===== Auto-Refresh Functionality =====

let autoRefreshInterval = null;

/**
 * Initialize auto-refresh toggle
 * 
 * @param {Function} refreshCallback - Function to call on refresh
 * @param {number} interval - Refresh interval in seconds
 */
function initAutoRefresh(refreshCallback, interval = 30) {
    const toggle = document.getElementById('auto-refresh-toggle');
    
    if (toggle) {
        toggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                startAutoRefresh(refreshCallback, interval);
            } else {
                stopAutoRefresh();
            }
        });
    }
}

/**
 * Start auto-refresh
 * 
 * @param {Function} callback - Function to call on refresh
 * @param {number} interval - Refresh interval in seconds
 */
function startAutoRefresh(callback, interval = 30) {
    stopAutoRefresh(); // Clear any existing interval
    
    autoRefreshInterval = setInterval(() => {
        console.log('Auto-refreshing data...');
        callback();
    }, interval * 1000);
    
    console.log(`Auto-refresh started (every ${interval} seconds)`);
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('Auto-refresh stopped');
    }
}

// ===== Loading Indicators =====

/**
 * Show loading spinner in element
 * 
 * @param {string|HTMLElement} element - Element or selector
 */
function showLoading(element) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    
    if (el) {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        el.style.position = 'relative';
        el.appendChild(overlay);
    }
}

/**
 * Hide loading spinner from element
 * 
 * @param {string|HTMLElement} element - Element or selector
 */
function hideLoading(element) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    
    if (el) {
        const overlay = el.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
}

// ===== Error/Success Messages =====

/**
 * Show error message
 * 
 * @param {string} message - Error message to display
 */
function showError(message) {
    showFlashMessage(message, 'error');
}

/**
 * Show success message
 * 
 * @param {string} message - Success message to display
 */
function showSuccess(message) {
    showFlashMessage(message, 'success');
}

/**
 * Show flash message
 * 
 * @param {string} message - Message to display
 * @param {string} type - Message type ('error', 'success', 'warning', 'info')
 */
function showFlashMessage(message, type = 'info') {
    const container = document.querySelector('main');
    
    if (!container) return;
    
    const icons = {
        error: 'error',
        success: 'check_circle',
        warning: 'warning',
        info: 'info'
    };
    
    const flash = document.createElement('div');
    flash.className = `flash-message flash-${type} mb-4`;
    flash.innerHTML = `
        <span class="material-symbols-outlined">${icons[type]}</span>
        <span>${message}</span>
    `;
    
    container.insertBefore(flash, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        flash.remove();
    }, 5000);
}

// ===== Chart Helpers =====

/**
 * Get Chart.js theme colors based on current theme
 * 
 * @returns {Object} - Object with color values
 */
function getChartColors() {
    const isDark = document.documentElement.classList.contains('dark');
    
    return {
        primary: isDark ? '#60a5fa' : '#3b82f6',
        success: isDark ? '#4ade80' : '#22c55e',
        warning: isDark ? '#fbbf24' : '#f59e0b',
        danger: isDark ? '#f87171' : '#ef4444',
        info: isDark ? '#38bdf8' : '#0ea5e9',
        text: isDark ? '#e5e7eb' : '#374151',
        grid: isDark ? '#374151' : '#e5e7eb',
        background: isDark ? '#1f2937' : '#ffffff'
    };
}

/**
 * Get default Chart.js options with theme support
 * 
 * @returns {Object} - Chart.js options object
 */
function getDefaultChartOptions() {
    const colors = getChartColors();
    
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: colors.text
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
                }
            },
            y: {
                ticks: {
                    color: colors.text
                },
                grid: {
                    color: colors.grid
                }
            }
        }
    };
}

// ===== Initialization =====

/**
 * Initialize common functionality when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initMobileMenu();
    
    console.log('Common utilities initialized');
});

// ===== Export for use in other scripts =====
window.dashboardUtils = {
    fetchData,
    postData,
    formatDate,
    formatDateForInput,
    getDateRange,
    formatNumber,
    formatPercent,
    formatCompactNumber,
    initAutoRefresh,
    startAutoRefresh,
    stopAutoRefresh,
    showLoading,
    hideLoading,
    showError,
    showSuccess,
    showFlashMessage,
    getChartColors,
    getDefaultChartOptions
};
