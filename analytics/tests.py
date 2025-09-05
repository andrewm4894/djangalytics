from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import json
from analytics.models import Event
from analytics.serializers import EventSerializer, EventCreateSerializer


class EventModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.event_data = {
            'event_name': 'test_event',
            'properties': {'user_id': 123, 'source': 'test'}
        }

    def test_event_creation(self):
        """Test creating an event with all fields"""
        event = Event.objects.create(**self.event_data)
        
        self.assertEqual(event.event_name, 'test_event')
        self.assertEqual(event.properties, {'user_id': 123, 'source': 'test'})
        self.assertIsInstance(event.timestamp, datetime)
        self.assertTrue(event.id)

    def test_event_creation_minimal(self):
        """Test creating an event with only required fields"""
        event = Event.objects.create(event_name='minimal_event')
        
        self.assertEqual(event.event_name, 'minimal_event')
        self.assertEqual(event.properties, {})
        self.assertIsInstance(event.timestamp, datetime)

    def test_event_str_representation(self):
        """Test the string representation of Event"""
        event = Event.objects.create(event_name='test_event')
        expected_str = f"test_event at {event.timestamp}"
        self.assertEqual(str(event), expected_str)

    def test_event_ordering(self):
        """Test that events are ordered by timestamp descending"""
        old_event = Event.objects.create(
            event_name='old_event',
            timestamp=timezone.now() - timedelta(hours=1)
        )
        new_event = Event.objects.create(
            event_name='new_event',
            timestamp=timezone.now()
        )
        
        events = Event.objects.all()
        self.assertEqual(events[0], new_event)
        self.assertEqual(events[1], old_event)

    def test_event_properties_json_field(self):
        """Test properties field handles complex JSON"""
        complex_properties = {
            'user_info': {
                'id': 123,
                'name': 'Test User',
                'preferences': ['analytics', 'dashboard']
            },
            'session': {
                'duration': 300,
                'pages_viewed': 5
            }
        }
        
        event = Event.objects.create(
            event_name='complex_event',
            properties=complex_properties
        )
        
        self.assertEqual(event.properties, complex_properties)
        self.assertEqual(event.properties['user_info']['name'], 'Test User')


class EventSerializerTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.event = Event.objects.create(
            event_name='test_event',
            properties={'user_id': 123, 'source': 'test'}
        )

    def test_event_serializer_serialization(self):
        """Test EventSerializer serializes model correctly"""
        serializer = EventSerializer(self.event)
        data = serializer.data
        
        self.assertEqual(data['event_name'], 'test_event')
        self.assertEqual(data['properties'], {'user_id': 123, 'source': 'test'})
        self.assertIn('id', data)
        self.assertIn('timestamp', data)

    def test_event_create_serializer_valid_data(self):
        """Test EventCreateSerializer with valid data"""
        event_data = {
            'event_name': 'serializer_test',
            'properties': {'key': 'value'}
        }
        serializer = EventCreateSerializer(data=event_data)
        
        self.assertTrue(serializer.is_valid())
        event = serializer.save()
        
        self.assertEqual(event.event_name, 'serializer_test')
        self.assertEqual(event.properties, {'key': 'value'})

    def test_event_create_serializer_missing_event_name(self):
        """Test EventCreateSerializer fails without event_name"""
        invalid_data = {'properties': {'key': 'value'}}
        serializer = EventCreateSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('event_name', serializer.errors)


class EventViewsTest(TestCase):
    def setUp(self):
        """Set up test client and sample data"""
        self.client = Client()
        
        # Create sample events for testing
        base_time = timezone.now()
        self.events_data = [
            {'event_name': 'user_signup', 'timestamp': base_time - timedelta(days=1)},
            {'event_name': 'user_login', 'timestamp': base_time - timedelta(hours=2)},
            {'event_name': 'page_view', 'timestamp': base_time - timedelta(hours=1)},
            {'event_name': 'user_signup', 'timestamp': base_time - timedelta(minutes=30)},
            {'event_name': 'button_click', 'timestamp': base_time},
        ]
        
        for event_data in self.events_data:
            Event.objects.create(**event_data)

    def test_capture_event_post_success(self):
        """Test successful event capture"""
        url = reverse('capture_event')
        data = {
            'event_name': 'test_event',
            'properties': {'user_id': 123, 'source': 'test'}
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        
        self.assertIn('id', response_data)
        self.assertEqual(response_data['event_name'], 'test_event')
        self.assertIn('timestamp', response_data)
        self.assertEqual(response_data['message'], 'Event captured successfully')
        
        # Verify event was created in database
        self.assertTrue(Event.objects.filter(event_name='test_event').exists())

    def test_capture_event_minimal_data(self):
        """Test event capture with minimal required data"""
        url = reverse('capture_event')
        data = {'event_name': 'minimal_event'}
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Verify event was created with default timestamp
        event = Event.objects.get(event_name='minimal_event')
        self.assertIsInstance(event.timestamp, datetime)
        self.assertEqual(event.properties, {})

    def test_capture_event_invalid_data(self):
        """Test event capture with invalid data"""
        url = reverse('capture_event')
        data = {}  # Missing required event_name
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('event_name', response_data)

    def test_get_stats_success(self):
        """Test successful stats retrieval"""
        url = reverse('get_stats')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Check response structure
        self.assertIn('daily_stats', response_data)
        self.assertIn('event_counts', response_data)
        self.assertIn('recent_events', response_data)
        self.assertIn('total_events', response_data)
        
        # Check total events count
        self.assertEqual(response_data['total_events'], len(self.events_data))

    def test_get_stats_event_counts(self):
        """Test that event counts are properly aggregated"""
        url = reverse('get_stats')
        
        response = self.client.get(url)
        response_data = response.json()
        
        event_counts = response_data['event_counts']
        
        # Find user_signup count (should be 2)
        signup_count = next(
            (item['count'] for item in event_counts if item['event_name'] == 'user_signup'),
            0
        )
        self.assertEqual(signup_count, 2)

    def test_get_events_success(self):
        """Test successful events retrieval"""
        url = reverse('get_events')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), len(self.events_data))
        
        # Check that each event has required fields
        for event in response_data:
            self.assertIn('id', event)
            self.assertIn('event_name', event)
            self.assertIn('timestamp', event)
            self.assertIn('properties', event)

    def test_stats_with_no_events(self):
        """Test stats endpoint when no events exist"""
        # Clear all events
        Event.objects.all().delete()
        
        url = reverse('get_stats')
        response = self.client.get(url)
        response_data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['total_events'], 0)
        self.assertEqual(len(response_data['event_counts']), 0)
        self.assertEqual(len(response_data['recent_events']), 0)