"""
Test script for API endpoints

This script tests all API endpoints to ensure they are working correctly.
"""

import sys
from app import create_app

def test_api_endpoints():
    """Test all API endpoints"""
    app = create_app()
    
    with app.test_client() as client:
        print("Testing API endpoints...")
        print("-" * 60)
        
        # Test /api/summary
        print("\n1. Testing GET /api/summary")
        response = client.get('/api/summary')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response keys: {list(data.keys())}")
            print(f"   Total posts: {data.get('total_posts')}")
            print(f"   Total comments: {data.get('total_comments')}")
            print(f"   Avg sentiment: {data.get('avg_sentiment')}")
        else:
            print(f"   Error: {response.get_json()}")
        
        # Test /api/sentiment
        print("\n2. Testing GET /api/sentiment")
        response = client.get('/api/sentiment')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response keys: {list(data.keys())}")
            if 'distribution' in data:
                print(f"   Distribution: {data['distribution']}")
        else:
            print(f"   Error: {response.get_json()}")
        
        # Test /api/sentiment with date range
        print("\n3. Testing GET /api/sentiment with date range")
        response = client.get('/api/sentiment?start_date=2024-01-01&end_date=2024-12-31')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Success with date range parameters")
        else:
            print(f"   Error: {response.get_json()}")
        
        # Test /api/engagement
        print("\n4. Testing GET /api/engagement")
        response = client.get('/api/engagement')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response keys: {list(data.keys())}")
            if 'top_posts' in data:
                print(f"   Top posts count: {len(data['top_posts'])}")
        else:
            print(f"   Error: {response.get_json()}")
        
        # Test /api/content
        print("\n5. Testing GET /api/content")
        response = client.get('/api/content')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response keys: {list(data.keys())}")
            if 'hashtags' in data:
                print(f"   Hashtags count: {len(data['hashtags'])}")
        else:
            print(f"   Error: {response.get_json()}")
        
        # Test /api/posts
        print("\n6. Testing GET /api/posts")
        response = client.get('/api/posts')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response keys: {list(data.keys())}")
            print(f"   Total posts: {data.get('total')}")
            print(f"   Page: {data.get('page')}")
            print(f"   Per page: {data.get('per_page')}")
            print(f"   Total pages: {data.get('total_pages')}")
        else:
            print(f"   Error: {response.get_json()}")
        
        # Test /api/posts with pagination
        print("\n7. Testing GET /api/posts with pagination")
        response = client.get('/api/posts?page=1&per_page=10')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Posts returned: {len(data.get('posts', []))}")
        else:
            print(f"   Error: {response.get_json()}")
        
        # Test /api/posts with search
        print("\n8. Testing GET /api/posts with search")
        response = client.get('/api/posts?search=test')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Success with search parameter")
        else:
            print(f"   Error: {response.get_json()}")
        
        # Test /api/posts with invalid parameters
        print("\n9. Testing GET /api/posts with invalid page number")
        response = client.get('/api/posts?page=-1')
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print(f"   Correctly returned 400 error")
            print(f"   Error message: {response.get_json().get('error')}")
        else:
            print(f"   Unexpected status code")
        
        # Test /api/posts with invalid date
        print("\n10. Testing GET /api/posts with invalid date")
        response = client.get('/api/posts?start_date=invalid-date')
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print(f"   Correctly returned 400 error")
            print(f"   Error message: {response.get_json().get('error')}")
        else:
            print(f"   Unexpected status code")
        
        # Test /api/export
        print("\n11. Testing GET /api/export")
        response = client.get('/api/export')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Content-Type: {response.content_type}")
            print(f"   Content-Length: {len(response.data)} bytes")
        else:
            print(f"   Error: {response.get_json()}")
        
        # Test CORS headers
        print("\n12. Testing CORS headers")
        response = client.get('/api/summary')
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        print(f"   Access-Control-Allow-Origin: {cors_header}")
        if cors_header:
            print(f"   CORS is enabled")
        else:
            print(f"   CORS header not found")
        
        print("\n" + "-" * 60)
        print("API endpoint testing complete!")

if __name__ == '__main__':
    try:
        test_api_endpoints()
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
