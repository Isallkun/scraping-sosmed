
import sys
import os
import logging
import requests
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from app import create_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_api():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # 1. Test /api/posts
        logger.info("Testing /api/posts endpoint...")
        try:
            response = client.get('/api/posts?page=1&per_page=10')
            if response.status_code == 200:
                data = response.get_json()
                logger.info(f"SUCCESS: Retrieved {len(data.get('posts', []))} posts")
                logger.info(f"Total posts: {data.get('total')}")
            else:
                logger.error(f"FAILURE: Status {response.status_code}")
                logger.error(f"Response: {response.get_data(as_text=True)}")
        except Exception as e:
            logger.error(f"EXCEPTION in /api/posts: {e}")

        # 2. Test /api/import (mock)
        logger.info("Testing /api/import endpoint (mock)...")
        # We need a dummy file
        dummy_csv = "post_id,platform,author,content,timestamp,likes,comments_count,shares,url,media_type\ntest_123,instagram,user1,content1,2023-01-01T12:00:00,10,2,0,http://url,post"
        
        data = {
            'file': (io.BytesIO(dummy_csv.encode('utf-8')), 'test.csv'),
            'platform': 'instagram'
        }
        
        try:
            response = client.post('/api/import', data=data, content_type='multipart/form-data')
            if response.status_code == 200:
                result = response.get_json()
                logger.info(f"SUCCESS: Import stats: {result.get('stats')}")
            else:
                logger.error(f"FAILURE: Status {response.status_code}")
                logger.error(f"Response: {response.get_data(as_text=True)}")
        except Exception as e:
            logger.error(f"EXCEPTION in /api/import: {e}")

import io
if __name__ == "__main__":
    debug_api()
