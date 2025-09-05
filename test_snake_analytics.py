#!/usr/bin/env python3
"""
Test script to simulate Snake game analytics events
"""
import requests
import json
import random
import time
from datetime import datetime, timedelta

# Test the Snake game analytics integration
BASE_URL = "http://localhost:8000/api"

def send_event(event_name, source="snake-game", properties=None):
    """Send an analytics event"""
    if properties is None:
        properties = {}
    
    event_data = {
        'event_name': event_name,
        'source': source,
        'timestamp': datetime.now().isoformat(),
        'properties': {
            'session_id': 'test_session_123',
            **properties
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/capture_event/", json=event_data)
        if response.status_code == 201:
            print(f"✓ Sent {source}.{event_name}: {properties}")
            return True
        else:
            print(f"✗ Failed to send {event_name}: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error sending {event_name}: {e}")
        return False

def simulate_snake_game_session():
    """Simulate a complete Snake game session with realistic events"""
    print("🐍 Simulating Snake Game Session...")
    
    # 1. App opened
    send_event('app_opened', properties={
        'screen_width': 1920,
        'screen_height': 1080,
        'user_agent': 'Test Browser'
    })
    
    time.sleep(0.5)
    
    # 2. Game started
    send_event('game_started', properties={
        'snake_length': 1,
        'current_score': 0,
        'high_score': 150
    })
    
    # 3. Simulate eating food multiple times
    score = 0
    snake_length = 1
    
    for i in range(random.randint(3, 8)):
        time.sleep(random.uniform(0.2, 1.0))  # Realistic timing between food
        score += 10
        snake_length += 1
        
        send_event('food_eaten', properties={
            'score': score,
            'snake_length': snake_length,
            'food_position': {'x': random.randint(0, 20), 'y': random.randint(0, 20)},
            'game_duration': (i + 1) * 2000  # Approximate game duration
        })
    
    # 4. Random direction changes
    directions = ['up', 'down', 'left', 'right']
    for _ in range(random.randint(2, 5)):
        time.sleep(0.1)
        send_event('direction_changed', properties={
            'new_direction': random.choice(directions),
            'score': score,
            'snake_length': snake_length
        })
    
    # 5. Maybe pause/resume
    if random.choice([True, False]):
        send_event('game_paused', properties={
            'score': score,
            'snake_length': snake_length,
            'game_duration': 10000
        })
        time.sleep(0.3)
        send_event('game_resumed', properties={
            'score': score,
            'snake_length': snake_length
        })
    
    # 6. High score achieved (sometimes)
    if score > 50:
        send_event('high_score_achieved', properties={
            'new_high_score': score,
            'previous_high_score': 150,
            'snake_length': snake_length,
            'game_duration': 15000
        })
    
    # 7. Game over
    final_duration = random.randint(10000, 30000)
    send_event('game_over', properties={
        'final_score': score,
        'high_score': max(150, score),
        'snake_length': snake_length,
        'game_duration': final_duration,
        'food_eaten': score // 10,
        'average_score_per_second': score / (final_duration / 1000)
    })

def simulate_multiple_sources():
    """Simulate events from multiple sources to test multi-source analytics"""
    print("\n📱 Simulating Multiple App Sources...")
    
    sources_and_events = {
        'web': ['user_signup', 'page_view', 'button_click', 'form_submit'],
        'mobile-app': ['app_launch', 'screen_view', 'tap_event', 'purchase'],
        'api': ['api_call', 'webhook_received', 'data_sync', 'error_logged'],
        'snake-game': ['game_started', 'food_eaten', 'game_over']
    }
    
    for source, events in sources_and_events.items():
        for _ in range(random.randint(2, 5)):
            event_name = random.choice(events)
            properties = {
                'source_version': f"{source}-v1.0",
                'user_id': random.randint(1, 100),
                'timestamp_local': datetime.now().isoformat()
            }
            
            # Add source-specific properties
            if source == 'snake-game':
                properties.update({
                    'score': random.randint(0, 200),
                    'snake_length': random.randint(1, 20)
                })
            elif source == 'mobile-app':
                properties.update({
                    'device_type': random.choice(['iPhone', 'Android']),
                    'app_version': '2.1.0'
                })
            elif source == 'api':
                properties.update({
                    'endpoint': random.choice(['/users', '/orders', '/analytics']),
                    'response_time': random.randint(50, 500)
                })
            
            send_event(event_name, source=source, properties=properties)
            time.sleep(0.1)

def check_analytics():
    """Check the current analytics data"""
    print("\n📊 Checking Analytics Dashboard...")
    
    try:
        response = requests.get(f"{BASE_URL}/stats/")
        if response.status_code == 200:
            data = response.json()
            
            print(f"📈 Total Events: {data['total_events']}")
            print(f"📋 Event Types: {len(data['event_counts'])}")
            print(f"🎯 Sources: {len(data.get('source_counts', []))}")
            
            print("\n🎯 Events by Source:")
            for source in data.get('source_counts', []):
                print(f"  - {source['source']}: {source['count']} events")
            
            print("\n🔥 Top Events:")
            for event in data['event_counts'][:5]:
                print(f"  - {event['event_name']}: {event['count']} times")
            
            print(f"\n🕒 Recent Events: {len(data['recent_events'])} shown")
            
        else:
            print(f"❌ Failed to fetch analytics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching analytics: {e}")

def main():
    print("🚀 Starting Multi-Source Analytics Test")
    print("=" * 50)
    
    # Test 1: Simulate Snake game sessions
    simulate_snake_game_session()
    time.sleep(1)
    
    # Test 2: Simulate events from multiple sources
    simulate_multiple_sources()
    time.sleep(1)
    
    # Test 3: Another Snake game session
    print("\n🐍 Second Snake Game Session...")
    simulate_snake_game_session()
    
    # Check results
    time.sleep(1)
    check_analytics()
    
    print("\n🎉 Test completed!")
    print("🔗 View the dashboard at: http://localhost:3000")
    print("🐍 Play Snake game at: http://localhost:8080")

if __name__ == "__main__":
    main()