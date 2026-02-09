"""
Example: Using the Instagram Scraper

This example demonstrates how to use the InstagramScraper class
to scrape posts from Instagram.

Note: This is for educational purposes only. Make sure to comply with
Instagram's Terms of Service and robots.txt when scraping.
"""

import os
import json
from dotenv import load_dotenv
from scraper.scrapers.instagram import InstagramScraper

# Load environment variables
load_dotenv()


def main():
    """Main function to demonstrate Instagram scraping."""
    
    # Get credentials from environment variables
    credentials = {
        'username': os.getenv('INSTAGRAM_USERNAME'),
        'password': os.getenv('INSTAGRAM_PASSWORD')
    }
    
    # Check if credentials are provided
    if not credentials['username'] or not credentials['password']:
        print("Error: Instagram credentials not found in environment variables")
        print("Please set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in your .env file")
        return
    
    # Target URL to scrape (example: a public profile)
    target_url = os.getenv('INSTAGRAM_TARGET_URL', 'https://www.instagram.com/explore/')
    
    # Number of posts to scrape
    limit = int(os.getenv('SCRAPER_MAX_POSTS', '10'))
    
    print(f"Instagram Scraper Example")
    print(f"=" * 50)
    print(f"Target URL: {target_url}")
    print(f"Post limit: {limit}")
    print(f"=" * 50)
    print()
    
    # Create scraper instance
    scraper = InstagramScraper(
        credentials=credentials,
        rate_limit=30,  # 30 requests per minute
        timeout=300,    # 5 minutes timeout
        headless=True,  # Run in headless mode
        max_retries=5   # Retry failed requests up to 5 times
    )
    
    try:
        print("Starting scraping process...")
        print()
        
        # Scrape posts
        result = scraper.scrape(
            target_url=target_url,
            limit=limit,
            authenticate=True
        )
        
        # Display results
        print(f"\nScraping Complete!")
        print(f"=" * 50)
        print(f"Platform: {result['metadata']['platform']}")
        print(f"Scraped at: {result['metadata']['scraped_at']}")
        print(f"Total posts: {result['metadata']['total_posts']}")
        print(f"Execution time: {result['metadata']['execution_time_ms']}ms")
        print(f"Errors encountered: {result['metadata']['errors_encountered']}")
        print()
        
        # Display sample posts
        if result['posts']:
            print(f"Sample Posts:")
            print(f"-" * 50)
            for i, post in enumerate(result['posts'][:3], 1):
                print(f"\nPost {i}:")
                print(f"  ID: {post['post_id']}")
                print(f"  Author: {post['author']}")
                print(f"  Content: {post['content'][:100]}..." if len(post['content']) > 100 else f"  Content: {post['content']}")
                print(f"  Likes: {post['likes']}")
                print(f"  Comments: {post['comments_count']}")
                print(f"  Hashtags: {', '.join(post['hashtags'][:5])}" if post['hashtags'] else "  Hashtags: None")
                print(f"  URL: {post['url']}")
        
        # Save results to file
        output_file = 'output/instagram_posts.json'
        os.makedirs('output', exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"\nError during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup is handled automatically by the scraper
        print("\nScraper closed.")


if __name__ == '__main__':
    main()
