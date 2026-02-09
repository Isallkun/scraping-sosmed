"""
Example: Using the Twitter Scraper

This example demonstrates how to use the TwitterScraper class
to scrape tweets from Twitter (X).

Note: This is for educational purposes only. Make sure to comply with
Twitter's Terms of Service and robots.txt when scraping.
"""

import os
import json
from dotenv import load_dotenv
from scraper.scrapers.twitter import TwitterScraper

# Load environment variables
load_dotenv()


def main():
    """Main function to demonstrate Twitter scraping."""
    
    # Get credentials from environment variables
    credentials = {
        'username': os.getenv('TWITTER_USERNAME'),
        'password': os.getenv('TWITTER_PASSWORD')
    }
    
    # Check if credentials are provided
    if not credentials['username'] or not credentials['password']:
        print("Error: Twitter credentials not found in environment variables")
        print("Please set TWITTER_USERNAME and TWITTER_PASSWORD in your .env file")
        return
    
    # Target URL to scrape (example: a public profile)
    target_url = os.getenv('TWITTER_TARGET_URL', 'https://twitter.com/explore')
    
    # Number of tweets to scrape
    limit = int(os.getenv('SCRAPER_MAX_POSTS', '10'))
    
    print(f"Twitter Scraper Example")
    print(f"=" * 50)
    print(f"Target URL: {target_url}")
    print(f"Tweet limit: {limit}")
    print(f"=" * 50)
    print()
    
    # Create scraper instance
    scraper = TwitterScraper(
        credentials=credentials,
        rate_limit=30,  # 30 requests per minute
        timeout=300,    # 5 minutes timeout
        headless=True,  # Run in headless mode
        max_retries=5   # Retry failed requests up to 5 times
    )
    
    try:
        print("Starting scraping process...")
        print()
        
        # Scrape tweets
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
        print(f"Total tweets: {result['metadata']['total_posts']}")
        print(f"Execution time: {result['metadata']['execution_time_ms']}ms")
        print(f"Errors encountered: {result['metadata']['errors_encountered']}")
        print()
        
        # Display sample tweets
        if result['posts']:
            print(f"Sample Tweets:")
            print(f"-" * 50)
            for i, tweet in enumerate(result['posts'][:3], 1):
                print(f"\nTweet {i}:")
                print(f"  ID: {tweet['post_id']}")
                print(f"  Author: @{tweet['author']}")
                print(f"  Content: {tweet['content'][:100]}..." if len(tweet['content']) > 100 else f"  Content: {tweet['content']}")
                print(f"  Likes: {tweet['likes']}")
                print(f"  Retweets: {tweet['retweets']}")
                print(f"  Replies: {tweet['replies']}")
                print(f"  Hashtags: {', '.join(tweet['hashtags'][:5])}" if tweet['hashtags'] else "  Hashtags: None")
                print(f"  URL: {tweet['url']}")
        
        # Save results to file
        output_file = 'output/twitter_posts.json'
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
