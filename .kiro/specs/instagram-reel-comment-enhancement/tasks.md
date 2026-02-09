# Implementation Plan: Instagram Reel Support & Comment Extraction Enhancement

## Overview

Implementasi enhancement untuk `scrape_instagram_simple.py` yang menambahkan dukungan Instagram Reels dan memperbaiki ekstraksi komentar. Tasks dibagi menjadi 3 fase utama: Reel Support, Comment Extraction, dan Testing/Verification.

## Tasks

- [ ] 1. Implement Reel Support in scrape_profile_simple()
  - [x] 1.1 Update link selector to include reels
    - Modify CSS selector from `a[href*="/p/"]` to `a[href*="/p/"], a[href*="/reel/"]`
    - Location: ~line 447-450 in scrape_profile_simple()
    - _Validates: Requirement 13.1_
  
  - [x] 1.2 Add post_type extraction logic
    - Add conditional logic to detect `/p/` vs `/reel/` in URL
    - Extract post_id correctly for both formats
    - Set post_type variable to "post" or "reel"
    - Location: ~line 462-467 in scrape_profile_simple()
    - _Validates: Requirement 13.2_
  
  - [x] 1.3 Update unique_posts tuple structure
    - Change from `(post_id, href)` to `(post_id, href, post_type)`
    - Update all references to this tuple throughout the function
    - Location: ~line 462-527 in scrape_profile_simple()
    - _Validates: Requirement 13.2_
  
  - [x] 1.4 Add post_type field to post_data dictionary
    - Add `'post_type': post_type` to post_data dict
    - Ensure field is included in JSON output
    - Location: Where post_data dict is created in scrape_profile_simple()
    - _Validates: Requirement 13.3_
  
  - [x] 1.5 Update metadata with post/reel counts
    - Add `'post_count'` field counting posts with post_type == 'post'
    - Add `'reel_count'` field counting posts with post_type == 'reel'
    - Update metadata dict in main() function
    - Location: ~line 529-663 in main()
    - _Validates: Requirement 13.4_
  
  - [x] 1.6 Update sample output display
    - Add post_type to console output when displaying sample posts
    - Show post_count and reel_count in summary
    - Location: ~line 640-660 in main()
    - _Validates: Requirement 13.4_

- [ ] 2. Implement Enhanced Comment Extraction
  - [x] 2.1 Create scrape_comments_from_post_dom() function
    - Implement WebDriverWait for comment section rendering
    - Add logic to click "View all comments" button (English + Indonesian)
    - Implement scroll within comment container (up to 5 times)
    - Add logic to click "Load more" button
    - Extract comment author from `<a href>` elements
    - Extract comment text from `<span dir="auto">` elements
    - Extract timestamps from `<time>` elements
    - Filter out captions, UI text, and empty comments
    - Return array of comment objects with author, text, timestamp
    - Location: New function, insert before scrape_comments_from_post()
    - _Validates: Requirement 14.1, 14.2, 14.3, 14.4, 14.5_
  
  - [x] 2.2 Create scrape_comments_from_post_js() function
    - Implement JavaScript-based DOM query using execute_script()
    - Query for `ul li` elements containing comments
    - Extract author, text, timestamp using JavaScript
    - Filter out invalid/empty comments in JavaScript
    - Return array of comment objects
    - Location: New function, insert after scrape_comments_from_post_dom()
    - _Validates: Requirement 14.6_
  
  - [x] 2.3 Refactor existing scrape_comments_from_post() to use strategies
    - Rename existing implementation to scrape_comments_from_post_json()
    - Create new scrape_comments_from_post() orchestrator function
    - Implement strategy pattern: try JSON → DOM → JavaScript
    - Add logging for which strategy succeeded
    - Return empty array if all strategies fail
    - Pass post_type parameter for better logging context
    - Location: ~line 305-433, refactor existing function
    - _Validates: Requirement 14.6, 14.7_
  
  - [x] 2.4 Update scrape_comments_from_post() calls
    - Add post_type parameter to all function calls
    - Ensure comments array is included in post_data
    - Location: All places where scrape_comments_from_post() is called
    - _Validates: Requirement 14.7_

- [ ] 3. Testing and Verification
  - [x] 3.1 Write unit tests for post_type extraction
    - Test URL with `/p/` returns post_type="post"
    - Test URL with `/reel/` returns post_type="reel"
    - Test unknown URL format is skipped
    - Test post_id extraction for both formats
    - Location: Create new test file tests/test_reel_support.py
    - _Validates: Requirement 13.1, 13.2_
  
  - [x] 3.2 Write unit tests for comment extraction
    - Test comment object structure (author, text, timestamp)
    - Test filtering of empty/invalid comments
    - Test Indonesian locale button selectors
    - Mock WebDriver responses for DOM extraction
    - Location: Create new test file tests/test_comment_extraction.py
    - _Validates: Requirement 14.4, 14.5_
  
  - [x] 3.3 Write integration test for mixed content scraping
    - Test scraping profile with both posts and reels
    - Verify post_count + reel_count = total_posts
    - Verify each post has correct post_type field
    - Verify comments array is populated
    - Location: Add to existing integration test or create new one
    - _Validates: Requirement 13.3, 13.4, 14.7_
  
  - [x] 3.4 Manual verification with real Instagram profile
    - Run: `python scrape_instagram_simple.py https://www.instagram.com/rusdi_sutejo/ 3`
    - Verify output JSON has mix of posts and reels
    - Verify comments arrays have actual text (not empty)
    - Verify metadata shows correct counts
    - Check console output for strategy success messages
    - Location: Manual testing
    - _Validates: All requirements_
  
  - [x] 3.5 Run sentiment analysis on enhanced output
    - Run sentiment analyzer on output JSON with comments
    - Verify sentiment analysis works on comment text
    - Verify no errors with new post_type field
    - Location: Manual testing with sentiment analyzer
    - _Validates: End-to-end pipeline_
  
  - [x] 3.6 Run existing test suite
    - Execute: `python -m pytest tests/ -v --tb=short`
    - Ensure all existing tests still pass
    - Fix any broken tests due to schema changes
    - Location: Existing test suite
    - _Validates: Backward compatibility_

- [ ] 4. Documentation Updates
  - [x] 4.1 Update README or usage documentation
    - Document new post_type field in output schema
    - Document enhanced comment extraction with 3 strategies
    - Add example output showing reels and comments
    - Update any schema diagrams or examples
    - Location: README.md or docs/USAGE_GUIDE.md
    - _Validates: User documentation_
  
  - [x] 4.2 Add inline code comments
    - Comment the 3 comment extraction strategies
    - Document post_type detection logic
    - Add docstrings to new functions
    - Location: scrape_instagram_simple.py
    - _Validates: Code maintainability_

## Notes

- All tasks reference specific requirements for traceability
- Tasks are ordered by dependency (Reel support → Comment extraction → Testing)
- Manual verification (3.4, 3.5) should be done after automated tests pass
- Existing functionality must remain intact (backward compatibility)
- Comment extraction adds 2-10 seconds per post depending on comment count
- Indonesian locale support is critical for target user base
- Empty comments array is valid fallback (graceful degradation)
