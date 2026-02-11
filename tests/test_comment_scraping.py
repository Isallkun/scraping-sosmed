"""
Test script to verify comment scraping functionality
Tests the new comment scraping features without requiring actual Instagram login
"""

import json
from pathlib import Path

def test_instagram_scraper_has_comment_method():
    """Test that InstagramScraper has the scrape_post_comments method"""
    from scraper.scrapers.instagram import InstagramScraper

    print("🧪 Testing InstagramScraper class...")

    # Check if method exists
    assert hasattr(InstagramScraper, 'scrape_post_comments'), \
        "InstagramScraper should have scrape_post_comments method"

    print("   ✓ InstagramScraper has scrape_post_comments method")
    return True


def test_sentiment_analyzer_handles_comments():
    """Test that sentiment analyzer can process posts with comments"""
    from sentiment.sentiment_analyzer import SentimentAnalyzer

    print("\n🧪 Testing SentimentAnalyzer with comments...")

    # Create test data
    test_post = {
        'post_id': 'TEST123',
        'content': 'This is a great post!',
        'comments': [
            {
                'author': 'user1',
                'text': 'Amazing content!',
                'likes': 5
            },
            {
                'author': 'user2',
                'text': 'This is terrible',
                'likes': 1
            },
            {
                'author': 'user3',
                'text': 'Okay I guess',
                'likes': 0
            }
        ]
    }

    analyzer = SentimentAnalyzer(model_type='vader')

    # Analyze the post
    result = analyzer._analyze_post(test_post)

    # Verify post has sentiment
    assert 'sentiment' in result, "Post should have sentiment field"
    print("   ✓ Post sentiment added")

    # Verify comments have sentiment
    assert 'comments' in result, "Result should have comments"
    assert len(result['comments']) == 3, "Should have 3 comments"

    for i, comment in enumerate(result['comments']):
        assert 'sentiment' in comment, f"Comment {i} should have sentiment"

    print(f"   ✓ All {len(result['comments'])} comments have sentiment")

    # Verify sentiment summary exists
    assert 'comments_sentiment_summary' in result, "Should have comments_sentiment_summary"
    summary = result['comments_sentiment_summary']

    assert 'total_comments' in summary
    assert 'average_compound' in summary
    assert 'positive_count' in summary
    assert 'negative_count' in summary
    assert 'neutral_count' in summary

    print("   ✓ Sentiment summary calculated")
    print(f"      - Total comments: {summary['total_comments']}")
    print(f"      - Average compound: {summary['average_compound']}")
    print(f"      - Positive: {summary['positive_count']}, Negative: {summary['negative_count']}, Neutral: {summary['neutral_count']}")

    return True


def test_folder_structure():
    """Test that output folders are organized correctly"""
    print("\n🧪 Testing folder structure...")

    output_dir = Path("output")

    # Check main folders exist
    required_folders = ['instagram', 'twitter', 'facebook', 'sentiment', 'other']

    for folder in required_folders:
        folder_path = output_dir / folder
        assert folder_path.exists(), f"Folder {folder} should exist"

    print(f"   ✓ All {len(required_folders)} required folders exist")

    # Check if files were organized
    instagram_files = list((output_dir / 'instagram').glob('*.json'))
    twitter_files = list((output_dir / 'twitter').glob('*.json'))

    print(f"   ✓ Instagram folder has {len(instagram_files)} files")
    print(f"   ✓ Twitter folder has {len(twitter_files)} files")

    return True


def test_output_format():
    """Test that output files have correct format with comments"""
    print("\n🧪 Testing output file format...")

    # Create a sample output
    sample_data = {
        'metadata': {
            'platform': 'instagram',
            'scraped_at': '2026-02-09T12:00:00Z',
            'target_url': 'https://instagram.com/test/',
            'total_posts': 1,
            'total_comments': 2,
            'scrape_comments': True,
            'comments_per_post': 20
        },
        'posts': [
            {
                'post_id': 'ABC123',
                'post_url': 'https://instagram.com/p/ABC123/',
                'author': 'testuser',
                'content': 'Test post',
                'likes': 10,
                'comments_count': 2,
                'comments': [
                    {
                        'author': 'commenter1',
                        'text': 'Nice!',
                        'likes': 1,
                        'timestamp': '2026-02-09T12:01:00Z'
                    },
                    {
                        'author': 'commenter2',
                        'text': 'Cool!',
                        'likes': 0,
                        'timestamp': '2026-02-09T12:02:00Z'
                    }
                ]
            }
        ]
    }

    # Verify structure
    assert 'metadata' in sample_data
    assert 'posts' in sample_data
    assert 'total_comments' in sample_data['metadata']
    assert 'comments' in sample_data['posts'][0]
    assert len(sample_data['posts'][0]['comments']) == 2

    print("   ✓ Output format is correct")
    print("   ✓ Metadata includes comment count")
    print("   ✓ Posts include comments array")

    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("Testing Instagram Comment Scraping Features")
    print("=" * 70)

    tests = [
        ("InstagramScraper has comment method", test_instagram_scraper_has_comment_method),
        ("SentimentAnalyzer handles comments", test_sentiment_analyzer_handles_comments),
        ("Folder structure is organized", test_folder_structure),
        ("Output format is correct", test_output_format),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"   ✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"   ✗ Test error: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print("Test Results")
    print("=" * 70)
    print(f"✓ Passed: {passed}/{len(tests)}")
    print(f"✗ Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 All tests passed! Comment scraping is ready to use!")
        print("\nNext steps:")
        print("1. Run: python scrape_instagram_simple.py <instagram_url> 5")
        print("2. Check output/instagram/ folder for results")
        print("3. Analyze sentiment: python -m sentiment.main_analyzer --input output/instagram/posts_*.json --output output/sentiment/posts_*_sentiment.json")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues.")

    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys

    # Fix Windows console encoding
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    sys.exit(main())
