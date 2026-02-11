"""Test the content endpoint specifically"""
from app import create_app

app = create_app()

with app.test_client() as client:
    response = client.get('/api/content')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.get_json()}")
