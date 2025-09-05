#!/usr/bin/env python
import requests
import json
from datetime import datetime, timedelta
import random

# Test the API endpoints
BASE_URL = "http://localhost:8000/api"

def test_capture_event():
    """Test capturing events"""
    events = [
        'user_signup',
        'user_login', 
        'page_view',
        'button_click',
        'form_submit',
        'purchase',
        'logout'
    ]
    
    print("Testing event capture...")
    
    # Create some test events from different sources
    sources = ['web', 'mobile-app', 'api', 'admin-panel']
    
    for i in range(20):
        event_data = {
            'event_name': random.choice(events),
            'source': random.choice(sources),
            'timestamp': (datetime.now() - timedelta(days=random.randint(0, 6))).isoformat(),
            'properties': {
                'user_id': random.randint(1, 100),
                'session_id': f'session_{random.randint(1000, 9999)}'
            }
        }
        
        response = requests.post(f"{BASE_URL}/capture_event/", json=event_data)
        if response.status_code == 201:
            print(f"✓ Captured event: {event_data['event_name']}")
        else:
            print(f"✗ Failed to capture event: {response.text}")

def test_get_stats():
    """Test getting statistics"""
    print("\nTesting stats endpoint...")
    
    response = requests.get(f"{BASE_URL}/stats/")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved stats:")
        print(f"  Total events: {data['total_events']}")
        print(f"  Event types: {len(data['event_counts'])}")
        print(f"  Daily stats entries: {len(data['daily_stats'])}")
        print(f"  Recent events: {len(data['recent_events'])}")
    else:
        print(f"✗ Failed to get stats: {response.text}")

if __name__ == "__main__":
    try:
        test_capture_event()
        test_get_stats()
        print("\n✓ API tests completed successfully!")
        print("Now you can open http://localhost:3000 to see the dashboard!")
    except requests.exceptions.ConnectionError:
        print("✗ Connection error. Make sure Django server is running on http://localhost:8000")