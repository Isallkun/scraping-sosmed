"""
Instagram Scraper - Simplified Script with Better Error Handling
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.scrapers.instagram import InstagramScraper
from scraper.config import get_config

def print_banner():
    """Print banner"""
    print("=" * 70)
    print("Instagram Scraper - Real Mode")
    print("=" * 70)
    print()

def load_credentials():
    """Load Instagram credentials from .env"""
    config = get_config()
    
    username = config.username or os.getenv('INSTAGRAM_USERNAME')
    password = config.password or os.getenv('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("❌ Error: Instagram credentials not found!")
        print()
        print("Please set credentials in .env file:")
        print("  INSTAGRAM_USERNAME=your_username")
        print("  INSTAGRAM_PASSWORD=your_password")
        print()
        sys.exit(1)
    
    return username, password

def scrape_instagram(target_url, limit=5, headless=False):
    """Scrape Instagram with better error handling"""
    
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print(f"Target: {target_url}")
    print(f"Limit: {limit} posts")
    print(f"Headless: {headless}")
    print()
    
    # Load credentials
    print("Loading credentials...")
    username, password = load_credentials()
    print(f"Credentials loaded for: {username}")
    print()
    
    # Initialize scraper
    print("Initializing Instagram scraper...")
    scraper = InstagramScraper(
        credentials={'username': username, 'password': password},
        rate_limit=20,  # Lower rate limit to avoid detection
        timeout=600,    # Longer timeout for authentication
        headless=headless
    )
    print("Scraper initialized")
    print()
    
    # Start scraping
    print("Starting scraping process...")
    print("   (This may take a few minutes...)")
    print()
    
    try:
        result = scraper.scrape(
            target_url=target_url,
            limit=limit,
            authenticate=True
        )
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"output/instagram_real_{timestamp}.json"
        
        Path("output").mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print()
        print("=" * 70)
        print("Scraping Completed Successfully!")
        print("=" * 70)
        print()
        print(f"Output: {output_path}")
        print(f"Posts scraped: {result['metadata']['total_posts']}")
        print(f"Execution time: {result['metadata'].get('execution_time_ms', 0)}ms")
        print()
        
        # Show sample posts
        if result['posts']:
            print("Sample Posts:")
            print("-" * 70)
            for i, post in enumerate(result['posts'][:3], 1):
                print(f"{i}. @{post['author']}")
                print(f"   {post['content'][:60]}...")
                print(f"   Likes: {post['likes']} | Comments: {post['comments_count']}")
                print()
        
        print("Next Steps:")
        print(f"1. Run sentiment analysis:")
        print(f"   python -m sentiment.main_analyzer --input {output_path} --output {output_path.replace('.json', '_sentiment.json')}")
        print()
        print(f"2. View results:")
        print(f"   python view_results.py {output_path.replace('.json', '_sentiment.json')}")
        print()
        
        return output_path
        
    except KeyboardInterrupt:
        print()
        print("WARNING: Scraping interrupted by user")
        return None
        
    except Exception as e:
        print()
        print("=" * 70)
        print("ERROR: Scraping Failed")
        print("=" * 70)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Common Issues:")
        print("1. Instagram detected automation - try again later")
        print("2. Invalid credentials - check .env file")
        print("3. 2FA enabled - disable temporarily")
        print("4. Rate limiting - wait a few minutes")
        print()
        print("Troubleshooting:")
        print("- Run with headless=False to see what's happening")
        print("- Check logs in logs/ directory")
        print("- Try demo mode: python demo_scraper.py")
        print()
        
        return None

def main():
    """Main function"""
    print_banner()
    
    # Configuration
    target_url = os.getenv('INSTAGRAM_TARGET_URL', 'https://www.instagram.com/rusdi_sutejo/')
    limit = 5
    headless = False  # Set to True for production
    
    # Allow command line override
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    if len(sys.argv) > 2:
        limit = int(sys.argv[2])
    if len(sys.argv) > 3:
        headless = sys.argv[3].lower() == 'true'
    
    # Run scraper
    result = scrape_instagram(target_url, limit, headless)
    
    if result:
        print("=" * 70)
        print("SUCCESS! Check the output file for results.")
        print("=" * 70)
    else:
        print("=" * 70)
        print("WARNING: Scraping did not complete. See error messages above.")
        print("=" * 70)

if __name__ == "__main__":
    main()
