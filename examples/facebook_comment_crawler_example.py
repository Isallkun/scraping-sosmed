"""
Example: Using the Facebook Comment Crawler (Playwright-based)

This example demonstrates how to use the FacebookCommentCrawler class
to crawl comments from Facebook posts and profiles.

Note: This is for educational purposes only. Make sure to comply with
Facebook's Terms of Service when scraping.

Prerequisites:
    pip install playwright
    playwright install chromium
"""

import os
from dotenv import load_dotenv
from scraper.scrapers.facebook_comments import FacebookCommentCrawler

# Load environment variables
load_dotenv()


def example_single_post():
    """Example: Crawl comments from a single Facebook post."""
    print("=" * 60)
    print("Example 1: Single Post Comment Crawling")
    print("=" * 60)

    crawler = FacebookCommentCrawler(
        headless=True,
        export_format='csv',
        export_mode='single',
    )

    result = crawler.crawl_comments(
        post_url="https://www.facebook.com/username/posts/123456789",
        max_comments=50,
    )

    print(f"\nResults:")
    print(f"  Total comments: {len(result['comments'])}")
    print(f"  Exported files: {result['exported_files']}")

    if result['comments']:
        print(f"\nSample comment:")
        comment = result['comments'][0]
        print(f"  Author: {comment.get('comment_author_name', 'N/A')}")
        print(f"  Text: {comment.get('comment_text', 'N/A')[:100]}")
        print(f"  Timestamp: {comment.get('comment_timestamp', 'N/A')}")


def example_profile_crawl():
    """Example: Crawl comments from all posts of a profile."""
    print("\n" + "=" * 60)
    print("Example 2: Profile Comment Crawling")
    print("=" * 60)

    crawler = FacebookCommentCrawler(
        headless=True,
        export_format='both',  # Export CSV + JSON
        export_mode='per-post',
    )

    result = crawler.crawl_from_profile(
        profile_url="https://www.facebook.com/username",
        max_posts=5,
        max_comments=20,
    )

    print(f"\nResults:")
    print(f"  Total comments: {len(result['comments'])}")
    print(f"  Stats: {result['stats']}")
    print(f"  Exported files:")
    for f in result['exported_files']:
        print(f"    - {f}")


def example_batch_urls():
    """Example: Crawl comments from multiple URLs in a file."""
    print("\n" + "=" * 60)
    print("Example 3: Batch URL Crawling")
    print("=" * 60)

    # First, create a sample URLs file
    urls_file = "data/facebook_comments/sample_urls.txt"
    os.makedirs(os.path.dirname(urls_file), exist_ok=True)

    with open(urls_file, 'w') as f:
        f.write("# Facebook post URLs (one per line)\n")
        f.write("https://www.facebook.com/user1/posts/111\n")
        f.write("https://www.facebook.com/user2/posts/222\n")

    crawler = FacebookCommentCrawler(
        headless=True,
        export_format='json',
    )

    result = crawler.crawl_from_file(
        urls_file=urls_file,
        max_comments=30,
    )

    print(f"\nResults:")
    print(f"  Total comments: {len(result['comments'])}")
    print(f"  Exported files: {result['exported_files']}")


def example_username_crawl():
    """Example: Crawl using just a Facebook username."""
    print("\n" + "=" * 60)
    print("Example 4: Username-based Crawling")
    print("=" * 60)

    crawler = FacebookCommentCrawler(
        headless=True,
        export_format='excel',
    )

    result = crawler.crawl_from_profile(
        username="FacebookUsername",
        max_posts=3,
        max_comments=10,
    )

    print(f"\nResults:")
    print(f"  Total comments: {len(result['comments'])}")
    print(f"  Exported files: {result['exported_files']}")


if __name__ == '__main__':
    print("Facebook Comment Crawler Examples")
    print("Make sure FB_COMMENT_EMAIL and FB_COMMENT_PASSWORD are set in .env\n")

    # Run example 1: Single post
    example_single_post()

    # Uncomment to run other examples:
    # example_profile_crawl()
    # example_batch_urls()
    # example_username_crawl()
