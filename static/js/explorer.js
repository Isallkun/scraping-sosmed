/**
 * Data Explorer Page JavaScript
 * 
 * Handles data table, search, filtering, sorting, pagination, and CSV export.
 */

// Current state
let currentPage = 1;
let perPage = 25;
let totalPages = 1;
let totalPosts = 0;
let currentSort = { column: 'timestamp', direction: 'desc' };
let currentFilters = {
    search: '',
    start_date: null,
    end_date: null,
    post_type: '',
    sentiment: ''
};

/**
 * Load posts data from API
 */
async function loadPostsData() {
    try {
        // Build query parameters
        const params = {
            page: currentPage,
            per_page: perPage,
            sort_by: currentSort.column,
            sort_order: currentSort.direction
        };
        // Add filters, mapping post_type to media_type for API
        if (currentFilters.search) params.search = currentFilters.search;
        if (currentFilters.start_date) params.start_date = currentFilters.start_date;
        if (currentFilters.end_date) params.end_date = currentFilters.end_date;
        if (currentFilters.post_type) params.media_type = currentFilters.post_type;
        if (currentFilters.sentiment) params.sentiment = currentFilters.sentiment;
        
        const data = await dashboardUtils.fetchData('/api/posts', params);
        updateTable(data.posts);
        updatePagination(data);
    } catch (error) {
        console.error('Failed to load posts data:', error);
        const tbody = document.getElementById('data-table-body');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-red-500">Failed to load data</td></tr>';
        }
    }
}

/**
 * Update data table
 */
function updateTable(posts) {
    const tbody = document.getElementById('data-table-body');
    if (!tbody) return;
    
    if (!posts || posts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-gray-500">No posts found</td></tr>';
        return;
    }
    
    tbody.innerHTML = posts.map(post => {
        const caption = post.content || '';
        const truncatedCaption = caption.length > 100 ? caption.substring(0, 100) + '...' : caption;

        // Determine sentiment badge
        let sentimentBadge = '';
        const score = Number(post.sentiment_score ?? 0);
        if (score > 0.05) {
            sentimentBadge = '<span class="badge badge-success">Positive</span>';
        } else if (score < -0.05) {
            sentimentBadge = '<span class="badge badge-danger">Negative</span>';
        } else {
            sentimentBadge = '<span class="badge badge-neutral">Neutral</span>';
        }

        // Post type badge
        const mediaType = post.media_type || 'post';
        const typeBadge = mediaType === 'reels'
            ? '<span class="badge badge-primary">Reel</span>'
            : '<span class="badge badge-neutral">Post</span>';

        return `
            <tr>
                <td class="font-medium">${post.author || 'Unknown'}</td>
                <td class="max-w-md">
                    <div class="truncate" title="${caption}">${truncatedCaption}</div>
                </td>
                <td class="text-right">${dashboardUtils.formatNumber(post.likes || 0)}</td>
                <td class="text-right">
                    <button class="text-blue-600 hover:text-blue-800 hover:underline focus:outline-none" 
                            onclick="openCommentsModal('${post.post_id}')">
                        ${dashboardUtils.formatNumber(post.comments_count || 0)}
                    </button>
                </td>
                <td class="text-center">
                    ${sentimentBadge}
                    <div class="text-xs text-gray-500 mt-1">${score.toFixed(3)}</div>
                </td>
                <td class="text-center">${typeBadge}</td>
                <td class="text-sm">${dashboardUtils.formatDate(post.timestamp, 'long')}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Update pagination controls
 */
function updatePagination(data) {
    currentPage = data.page || 1;
    totalPages = data.total_pages || 1;
    totalPosts = data.total || 0;
    
    // Update results summary
    const start = totalPosts > 0 ? ((currentPage - 1) * perPage) + 1 : 0;
    const end = Math.min(currentPage * perPage, totalPosts);
    
    document.getElementById('results-start').textContent = start;
    document.getElementById('results-end').textContent = end;
    document.getElementById('results-total').textContent = totalPosts;
    
    // Update page info
    document.getElementById('current-page').textContent = currentPage;
    document.getElementById('total-pages').textContent = totalPages;
    
    // Update button states
    document.getElementById('first-page').disabled = currentPage === 1;
    document.getElementById('prev-page').disabled = currentPage === 1;
    document.getElementById('next-page').disabled = currentPage === totalPages;
    document.getElementById('last-page').disabled = currentPage === totalPages;
    
    // Generate page numbers
    generatePageNumbers();
}

/**
 * Generate page number buttons
 */
function generatePageNumbers() {
    const container = document.getElementById('page-numbers');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Show max 5 page numbers
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    
    // Adjust if we're near the end
    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const button = document.createElement('button');
        button.className = `pagination-button ${i === currentPage ? 'active' : ''}`;
        button.textContent = i;
        button.addEventListener('click', () => goToPage(i));
        container.appendChild(button);
    }
}

/**
 * Go to specific page
 */
function goToPage(page) {
    if (page < 1 || page > totalPages || page === currentPage) return;
    currentPage = page;
    loadPostsData();
}

/**
 * Handle search
 */
function handleSearch() {
    const searchInput = document.getElementById('search-input');
    currentFilters.search = searchInput.value.trim();
    currentPage = 1; // Reset to first page
    loadPostsData();
}

/**
 * Apply filters
 */
function applyFilters() {
    currentFilters.start_date = document.getElementById('filter-start-date').value || null;
    currentFilters.end_date = document.getElementById('filter-end-date').value || null;
    currentFilters.post_type = document.getElementById('filter-post-type').value || '';
    currentFilters.sentiment = document.getElementById('filter-sentiment').value || '';
    
    currentPage = 1; // Reset to first page
    loadPostsData();
}

/**
 * Clear all filters
 */
function clearFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('filter-start-date').value = '';
    document.getElementById('filter-end-date').value = '';
    document.getElementById('filter-post-type').value = '';
    document.getElementById('filter-sentiment').value = '';
    
    currentFilters = {
        search: '',
        start_date: null,
        end_date: null,
        post_type: '',
        sentiment: ''
    };
    
    currentPage = 1;
    loadPostsData();
}

/**
 * Comments Modal Functions
 */
function openCommentsModal(postId) {
    const modal = document.getElementById('comments-modal');
    if (modal) {
        modal.classList.remove('hidden');
        loadComments(postId);
    }
}

function closeCommentsModal() {
    const modal = document.getElementById('comments-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

async function loadComments(postId) {
    const listContainer = document.getElementById('comments-list');
    if (!listContainer) return;

    listContainer.innerHTML = '<div class="text-center py-8 text-gray-500">Loading comments...</div>';

    try {
        // Use the platform ID (postId) in the URL
        const comments = await dashboardUtils.fetchData(`/api/posts/${postId}/comments`);
        renderComments(comments);
    } catch (error) {
        console.error('Failed to load comments:', error);
        listContainer.innerHTML = '<div class="text-center py-8 text-red-500">Failed to load comments</div>';
    }
}

function renderComments(comments) {
    const listContainer = document.getElementById('comments-list');
    if (!listContainer) return;

    if (!comments || comments.length === 0) {
        listContainer.innerHTML = '<div class="text-center py-8 text-gray-500">No comments found</div>';
        return;
    }

    const html = comments.map(comment => `
        <div class="border-b border-gray-200 dark:border-gray-700 py-3 last:border-0">
            <div class="flex justify-between items-start mb-1">
                <span class="font-semibold text-sm text-gray-900 dark:text-white">${comment.author || 'Unknown'}</span>
                <span class="text-xs text-gray-500">${dashboardUtils.formatDate(comment.timestamp)}</span>
            </div>
            <p class="text-sm text-gray-700 dark:text-gray-300 break-words">${comment.content || ''}</p>
        </div>
    `).join('');

    listContainer.innerHTML = html;
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initial load
    loadPostsData();

    // Search and filter listeners
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSearch();
        });
    }

    const searchBtn = document.getElementById('search-button');
    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearch);
    }

    const applyFiltersBtn = document.getElementById('apply-filters-button');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }

    const clearFiltersBtn = document.getElementById('clear-button');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearFilters);
    }

    const perPageSelect = document.getElementById('per-page-select');
    if (perPageSelect) {
        perPageSelect.addEventListener('change', (e) => {
            perPage = parseInt(e.target.value);
            currentPage = 1;
            loadPostsData();
        });
    }

    // Modal listeners
    const closeBtn = document.getElementById('close-comments-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeCommentsModal);
    }

    const modal = document.getElementById('comments-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeCommentsModal();
            }
        });
    }

    // Export functionality
    const exportBtn = document.getElementById('export-button');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            const params = new URLSearchParams();
            if (currentFilters.search) params.set('search', currentFilters.search);
            if (currentFilters.start_date) params.set('start_date', currentFilters.start_date);
            if (currentFilters.end_date) params.set('end_date', currentFilters.end_date);
            if (currentFilters.post_type) params.set('media_type', currentFilters.post_type);
            if (currentFilters.sentiment) params.set('sentiment', currentFilters.sentiment);
            const queryString = params.toString();
            const url = queryString ? `/api/export?${queryString}` : '/api/export';
            window.location.href = url;
        });
    }

    // Sortable column headers
    document.querySelectorAll('.sortable[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.getAttribute('data-sort');
            if (currentSort.column === column) {
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.column = column;
                currentSort.direction = 'desc';
            }
            currentPage = 1;
            loadPostsData();
        });
    });


    // Import functionality with modal
    const importBtn = document.getElementById('import-button');
    const importModal = document.getElementById('import-modal');
    const closeImportModal = document.getElementById('close-import-modal');
    const cancelImportBtn = document.getElementById('cancel-import-button');
    const confirmImportBtn = document.getElementById('confirm-import-button');
    const importFileInput = document.getElementById('import-file-input');
    const clearExistingCheckbox = document.getElementById('clear-existing-checkbox');
    const platformSelect = document.getElementById('import-platform-select');

    // Open modal when import button clicked
    if (importBtn) {
        importBtn.addEventListener('click', () => {
            importModal.classList.remove('hidden');
        });
    }

    // Close modal handlers
    if (closeImportModal) {
        closeImportModal.addEventListener('click', () => {
            importModal.classList.add('hidden');
            importFileInput.value = '';
        });
    }

    if (cancelImportBtn) {
        cancelImportBtn.addEventListener('click', () => {
            importModal.classList.add('hidden');
            importFileInput.value = '';
        });
    }

    // Close modal when clicking outside
    if (importModal) {
        importModal.addEventListener('click', (e) => {
            if (e.target === importModal) {
                importModal.classList.add('hidden');
                importFileInput.value = '';
            }
        });
    }

    // Confirm import
    if (confirmImportBtn) {
        confirmImportBtn.addEventListener('click', async () => {
            const file = importFileInput.files[0];
            
            if (!file) {
                alert('Please select a file to import');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);
            formData.append('platform', platformSelect.value);
            formData.append('clear_existing', clearExistingCheckbox.checked ? 'true' : 'false');

            // Show loading state
            const originalBtnText = confirmImportBtn.innerHTML;
            confirmImportBtn.disabled = true;
            confirmImportBtn.innerHTML = '<span class="loading-spinner w-4 h-4 mr-2"></span>Importing...';

            try {
                const response = await fetch('/api/import', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    // Build success message
                    const stats = result.stats || {};
                    let message = `Import successful!\n\n`;
                    message += `Total: ${stats.total || 0}\n`;
                    message += `Inserted: ${stats.inserted || 0}\n`;
                    message += `Skipped: ${stats.skipped || 0}\n`;
                    
                    if (stats.cleared) {
                        message += `\n🗑️ Cleared before import:\n`;
                        message += `  - Posts: ${stats.cleared.posts || 0}\n`;
                        message += `  - Sentiments: ${stats.cleared.sentiments || 0}\n`;
                        message += `  - Comments: ${stats.cleared.comments || 0}`;
                    }
                    
                    alert(message);

                    // Close modal and refresh data
                    importModal.classList.add('hidden');
                    importFileInput.value = '';
                    loadPostsData();
                } else {
                    alert(`Import failed: ${result.error || 'Unknown error'}`);
                }
            } catch (error) {
                console.error('Import error:', error);
                alert('An error occurred during import. Please try again.');
            } finally {
                // Restore button state
                confirmImportBtn.disabled = false;
                confirmImportBtn.innerHTML = originalBtnText;
            }
        });
    }

    // Scrape functionality
    const scrapeBtn = document.getElementById('scrape-button');
    const scrapeModal = document.getElementById('scrape-modal');
    const closeScrapeModal = document.getElementById('close-scrape-modal');
    const cancelScrapeBtn = document.getElementById('cancel-scrape-button');
    const confirmScrapeBtn = document.getElementById('confirm-scrape-button');
    const scrapeTargetUrl = document.getElementById('scrape-target-url');
    const scrapeLimit = document.getElementById('scrape-limit');
    const scrapeCommentsCheckbox = document.getElementById('scrape-comments-checkbox');
    const runSentimentCheckbox = document.getElementById('run-sentiment-checkbox');
    const autoImportCheckbox = document.getElementById('auto-import-checkbox');
    const scrapeClearExistingCheckbox = document.getElementById('scrape-clear-existing-checkbox');

    // Open scrape modal
    if (scrapeBtn) {
        scrapeBtn.addEventListener('click', () => {
            scrapeModal.classList.remove('hidden');
        });
    }

    // Close scrape modal handlers
    if (closeScrapeModal) {
        closeScrapeModal.addEventListener('click', () => {
            scrapeModal.classList.add('hidden');
        });
    }

    if (cancelScrapeBtn) {
        cancelScrapeBtn.addEventListener('click', () => {
            scrapeModal.classList.add('hidden');
        });
    }

    // Close modal when clicking outside
    if (scrapeModal) {
        scrapeModal.addEventListener('click', (e) => {
            if (e.target === scrapeModal) {
                scrapeModal.classList.add('hidden');
            }
        });
    }

    // Confirm scrape
    if (confirmScrapeBtn) {
        confirmScrapeBtn.addEventListener('click', async () => {
            const targetUrl = scrapeTargetUrl.value.trim();
            const limit = parseInt(scrapeLimit.value);

            // Validation
            if (!targetUrl) {
                alert('Please enter an Instagram profile URL');
                return;
            }

            if (!targetUrl.includes('instagram.com')) {
                alert('Please enter a valid Instagram URL');
                return;
            }

            if (limit < 1 || limit > 50) {
                alert('Number of posts must be between 1 and 50');
                return;
            }

            // Build form data
            const formData = new FormData();
            formData.append('target_url', targetUrl);
            formData.append('limit', limit);
            formData.append('scrape_comments', scrapeCommentsCheckbox.checked ? 'true' : 'false');
            formData.append('run_sentiment', runSentimentCheckbox.checked ? 'true' : 'false');
            formData.append('auto_import', autoImportCheckbox.checked ? 'true' : 'false');
            formData.append('clear_existing', scrapeClearExistingCheckbox.checked ? 'true' : 'false');

            // Show loading state
            const originalBtnText = confirmScrapeBtn.innerHTML;
            confirmScrapeBtn.disabled = true;
            confirmScrapeBtn.innerHTML = '<span class="loading-spinner w-4 h-4 mr-2"></span>Scraping... (this may take 2-5 minutes)';

            try {
                const response = await fetch('/api/scrape', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    // Build success message
                    let message = result.message || 'Scraping completed successfully!';
                    
                    if (result.scraping) {
                        message += `\n\nScraping Results:`;
                        message += `\n  - Posts scraped: ${result.scraping.posts_scraped}`;
                        message += `\n  - Sentiment analysis: ${result.scraping.sentiment_run ? 'Yes' : 'No'}`;
                    }

                    if (result.import) {
                        message += `\n\nImport Results:`;
                        message += `\n  - Total: ${result.import.total}`;
                        message += `\n  - Inserted: ${result.import.inserted}`;
                        message += `\n  - Skipped: ${result.import.skipped}`;
                        
                        if (result.import.cleared) {
                            message += `\n\nCleared before import:`;
                            message += `\n  - Posts: ${result.import.cleared.posts}`;
                            message += `\n  - Sentiments: ${result.import.cleared.sentiments}`;
                            message += `\n  - Comments: ${result.import.cleared.comments}`;
                        }
                    }

                    alert(message);

                    // Close modal and refresh data
                    scrapeModal.classList.add('hidden');
                    if (autoImportCheckbox.checked) {
                        loadPostsData(); // Refresh the table
                    }
                } else {
                    alert(`Scraping failed: ${result.error || 'Unknown error'}\n\nPlease check:\n- Instagram credentials in .env file\n- Internet connection\n- Instagram URL is valid`);
                }
            } catch (error) {
                console.error('Scraping error:', error);
                alert('An error occurred during scraping. Please check the console for details and try again.');
            } finally {
                // Restore button state
                confirmScrapeBtn.disabled = false;
                confirmScrapeBtn.innerHTML = originalBtnText;
            }
        });
    }
});
