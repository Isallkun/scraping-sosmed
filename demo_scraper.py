"""
Demo Script - Social Media Scraper
Demonstrates basic scraping functionality with mock data
"""

import json
from datetime import datetime
from pathlib import Path

def create_demo_data():
    """Create demo scraped data"""
    demo_posts = [
        {
            "post_id": "demo_001",
            "author": "rusdi_sutejo",
            "content": "Excited to share our latest project! 🚀 #innovation #technology",
            "timestamp": "2026-02-08T10:30:00Z",
            "likes": 245,
            "comments_count": 32,
            "hashtags": ["#innovation", "#technology"]
        },
        {
            "post_id": "demo_002",
            "author": "rusdi_sutejo",
            "content": "Great meeting with the team today. Productivity at its best! 💪",
            "timestamp": "2026-02-07T15:45:00Z",
            "likes": 189,
            "comments_count": 18,
            "hashtags": []
        },
        {
            "post_id": "demo_003",
            "author": "rusdi_sutejo",
            "content": "Beautiful sunset view from the office. Nature is amazing! 🌅",
            "timestamp": "2026-02-06T18:20:00Z",
            "likes": 412,
            "comments_count": 56,
            "hashtags": ["#sunset", "#nature"]
        },
        {
            "post_id": "demo_004",
            "author": "rusdi_sutejo",
            "content": "Disappointed with the service today. Not what I expected. 😞",
            "timestamp": "2026-02-05T12:10:00Z",
            "likes": 87,
            "comments_count": 23,
            "hashtags": []
        },
        {
            "post_id": "demo_005",
            "author": "rusdi_sutejo",
            "content": "Just another day at work. Nothing special happening.",
            "timestamp": "2026-02-04T09:00:00Z",
            "likes": 156,
            "comments_count": 12,
            "hashtags": ["#work"]
        }
    ]
    
    return {
        "metadata": {
            "platform": "instagram",
            "scraped_at": datetime.utcnow().isoformat() + "Z",
            "target_url": "https://www.instagram.com/rusdi_sutejo/",
            "total_posts": len(demo_posts),
            "execution_time_ms": 1250,
            "errors_encountered": 0,
            "note": "This is demo data for testing purposes"
        },
        "posts": demo_posts
    }

def save_demo_data(output_path):
    """Save demo data to file"""
    data = create_demo_data()
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return output_path, data

def main():
    """Main demo function"""
    print("=" * 60)
    print("Social Media Scraper - Demo Mode")
    print("=" * 60)
    print()
    
    # Generate demo data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"output/demo_instagram_posts_{timestamp}.json"
    
    print(f"Creating demo scraped data...")
    print(f"Output: {output_path}")
    print()
    
    output_file, data = save_demo_data(output_path)
    
    print("[OK] Demo data created successfully!")
    print()
    print("Summary:")
    print(f"  Platform: {data['metadata']['platform']}")
    print(f"  Total posts: {data['metadata']['total_posts']}")
    print(f"  Target: {data['metadata']['target_url']}")
    print()
    
    # Display sample posts
    print("Sample Posts:")
    print("-" * 60)
    for i, post in enumerate(data['posts'][:3], 1):
        print(f"\n{i}. {post['author']} ({post['timestamp']})")
        content_safe = post['content'][:60].encode('ascii', 'replace').decode('ascii')
        print(f"   {content_safe}...")
        print(f"   {post['likes']} likes | {post['comments_count']} comments")
    
    print()
    print("-" * 60)
    print()
    print("Next Steps:")
    print("1. Run sentiment analysis:")
    print(f"   python -m sentiment.main_analyzer --input {output_path} --output {output_path.replace('.json', '_sentiment.json')}")
    print()
    print("2. Or use the batch script:")
    print(f"   run_sentiment.bat {output_path}")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
