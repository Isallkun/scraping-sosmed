# Requirements Document: Instagram Reel Support & Comment Extraction Enhancement

## Introduction

Enhancement untuk Instagram scraper (`scrape_instagram_simple.py`) yang menambahkan dukungan untuk scraping Instagram Reels dan memperbaiki ekstraksi teks komentar. Saat ini scraper hanya mengambil posts reguler (`/p/`) dan melewatkan reels (`/reel/`), serta hanya mendapatkan jumlah komentar tanpa teks komentar yang sebenarnya.

## Glossary

- **Reel**: Format video pendek Instagram yang mirip dengan TikTok, memiliki URL pattern `/reel/{id}`
- **Post**: Format posting reguler Instagram dengan URL pattern `/p/{id}`
- **post_type**: Field yang mengidentifikasi apakah konten adalah "post" atau "reel"
- **Comment Extraction**: Proses mengambil teks komentar, author, dan timestamp dari post/reel
- **Lazy Loading**: Teknik Instagram untuk memuat komentar secara bertahap saat user scroll
- **DOM Extraction**: Metode mengambil data langsung dari Document Object Model browser
- **WebDriverWait**: Selenium utility untuk menunggu elemen muncul sebelum interaksi

## Requirements

### Requirement 13: Instagram Reel Support

**User Story:** As a data analyst, I want to scrape Instagram Reels in addition to regular posts, so that I can analyze all content types from a profile.

#### Acceptance Criteria

1. WHEN the Scraper searches for Instagram content, THE Scraper SHALL detect both post links (a[href*="/p/"]) and reel links (a[href*="/reel/"])
2. WHEN extracting post data, THE Scraper SHALL determine the post_type as either "post" or "reel" based on the URL format
3. WHEN storing scraped data, THE Scraper SHALL include the post_type field in the output JSON
4. WHEN scraping completes, THE Scraper SHALL report counts for both posts and reels separately in metadata

### Requirement 14: Improved Instagram Comment Extraction

**User Story:** As a data analyst, I want to extract actual comment text from Instagram posts and reels, so that I can perform sentiment analysis on user comments.

#### Acceptance Criteria

1. WHEN scraping an Instagram post or reel, THE Scraper SHALL wait for the comment section to render before attempting extraction
2. WHEN the "View all N comments" button is present, THE Scraper SHALL click it to expand comments
3. WHEN comments are lazy-loaded, THE Scraper SHALL scroll within the comment container and click "Load more" up to 5 times
4. WHEN extracting comment data, THE Scraper SHALL capture comment text, author username, and timestamp
5. WHEN parsing comments, THE Scraper SHALL filter out captions, UI text, and non-comment elements
6. WHEN comment extraction fails with DOM selectors, THE Scraper SHALL attempt JavaScript-based DOM query as a fallback
7. WHEN comment extraction completes, THE Scraper SHALL include an array of comment objects in the post data
