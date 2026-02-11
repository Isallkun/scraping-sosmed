"""
View Results - Display sentiment analysis results in a readable format
"""

import json
import sys
from pathlib import Path
from collections import Counter

def load_results(file_path):
    """Load results from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def display_summary(data):
    """Display summary statistics"""
    metadata = data['metadata']
    posts = data['posts']
    
    print("=" * 70)
    print("SENTIMENT ANALYSIS RESULTS")
    print("=" * 70)
    print()
    
    # Metadata
    print("📊 Summary:")
    print(f"   Platform: {metadata['platform']}")
    print(f"   Target: {metadata['target_url']}")
    print(f"   Total Posts: {metadata['total_posts']}")
    print(f"   Analyzed At: {metadata.get('analyzed_at', 'N/A')}")
    print(f"   Model: {metadata.get('sentiment_model', 'N/A')}")
    print()
    
    # Sentiment distribution
    if 'sentiment' in posts[0]:
        sentiments = [post['sentiment']['label'] for post in posts]
        sentiment_counts = Counter(sentiments)
        
        print("😊 Sentiment Distribution:")
        for label, count in sentiment_counts.items():
            percentage = (count / len(posts)) * 100
            emoji = "😊" if label == "positive" else "😞" if label == "negative" else "😐"
            print(f"   {emoji} {label.capitalize()}: {count} ({percentage:.1f}%)")
        print()
        
        # Average scores
        avg_compound = sum(post['sentiment']['compound'] for post in posts) / len(posts)
        print(f"📈 Average Sentiment Score: {avg_compound:.3f}")
        print()

def display_posts(data, limit=None):
    """Display individual posts with sentiment"""
    posts = data['posts']
    if limit:
        posts = posts[:limit]
    
    print("-" * 70)
    print("POSTS WITH SENTIMENT ANALYSIS")
    print("-" * 70)
    print()
    
    for i, post in enumerate(posts, 1):
        # Post info
        print(f"{i}. @{post['author']} - {post['timestamp']}")
        print(f"   {post['content']}")
        print(f"   ❤️ {post['likes']} likes | 💬 {post['comments_count']} comments")
        
        # Sentiment
        if 'sentiment' in post:
            sentiment = post['sentiment']
            label = sentiment['label']
            score = sentiment['compound']
            
            # Emoji based on sentiment
            emoji = "😊" if label == "positive" else "😞" if label == "negative" else "😐"
            
            print(f"   {emoji} Sentiment: {label.upper()} (score: {score:.3f})")
            print(f"      Positive: {sentiment['positive']:.3f} | "
                  f"Neutral: {sentiment['neutral']:.3f} | "
                  f"Negative: {sentiment['negative']:.3f}")
        
        print()

def display_insights(data):
    """Display insights and recommendations"""
    posts = data['posts']
    
    if 'sentiment' not in posts[0]:
        return
    
    print("-" * 70)
    print("💡 INSIGHTS")
    print("-" * 70)
    print()
    
    # Most positive post
    most_positive = max(posts, key=lambda p: p['sentiment']['compound'])
    print("🌟 Most Positive Post:")
    print(f"   \"{most_positive['content'][:60]}...\"")
    print(f"   Score: {most_positive['sentiment']['compound']:.3f}")
    print()
    
    # Most negative post
    most_negative = min(posts, key=lambda p: p['sentiment']['compound'])
    print("⚠️  Most Negative Post:")
    print(f"   \"{most_negative['content'][:60]}...\"")
    print(f"   Score: {most_negative['sentiment']['compound']:.3f}")
    print()
    
    # Engagement vs Sentiment
    avg_likes_positive = sum(p['likes'] for p in posts if p['sentiment']['label'] == 'positive') / max(1, sum(1 for p in posts if p['sentiment']['label'] == 'positive'))
    avg_likes_negative = sum(p['likes'] for p in posts if p['sentiment']['label'] == 'negative') / max(1, sum(1 for p in posts if p['sentiment']['label'] == 'negative'))
    
    print("📊 Engagement Analysis:")
    print(f"   Average likes on positive posts: {avg_likes_positive:.0f}")
    print(f"   Average likes on negative posts: {avg_likes_negative:.0f}")
    print()

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python view_results.py <results_file.json>")
        print()
        print("Example:")
        print("  python view_results.py output/demo_instagram_posts_20260209_083538_sentiment.json")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Load and display results
    data = load_results(file_path)
    
    display_summary(data)
    display_posts(data, limit=5)  # Show first 5 posts
    display_insights(data)
    
    print("=" * 70)
    print()
    
    # Show remaining posts count
    if len(data['posts']) > 5:
        print(f"Note: Showing 5 of {len(data['posts'])} posts. ")
        print(f"      View full results in: {file_path}")
        print()

if __name__ == "__main__":
    main()
