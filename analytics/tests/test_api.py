from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json
from unittest.mock import patch

from analytics.models import Project, Event, IPRateLimit, ProjectRateLimit


class EventAPITest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.project = Project.objects.create(
            name='Test Project',
            slug='test-project',
            rate_limit_per_minute=10
        )
        
        # Create some test events
        self.events_data = [
            {'event_name': 'user_signup', 'source': 'web'},
            {'event_name': 'user_login', 'source': 'mobile'},
            {'event_name': 'user_signup', 'source': 'web'},
        ]
        
        for event_data in self.events_data:
            Event.objects.create(
                project=self.project,
                **event_data,
                user_id='test_user',
                session_id='test_session'
            )

    def test_capture_event_success(self):
        """Test successful event capture with all fields"""
        url = reverse('capture_event')
        event_data = {
            'event_name': 'api_test_event',
            'source': 'web',
            'api_key': self.project.api_key,
            'properties': {'test': 'value'}
        }
        
        response = self.client.post(
            url, 
            json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        
        # Check response structure
        self.assertIn('id', response_data)
        self.assertIn('event_name', response_data)
        self.assertIn('timestamp', response_data)
        self.assertIn('user_id', response_data)
        self.assertIn('session_id', response_data)
        self.assertIn('ip_address', response_data)
        self.assertIn('user_agent', response_data)
        self.assertIn('rate_limit_info', response_data)
        self.assertIn('message', response_data)
        
        # Verify event was created in database
        event = Event.objects.get(id=response_data['id'])
        self.assertEqual(event.event_name, 'api_test_event')
        self.assertEqual(event.source, 'web')
        self.assertEqual(event.project, self.project)
        self.assertTrue(event.user_id.startswith('anon_'))
        self.assertTrue(event.session_id.startswith('anon_'))

    def test_capture_event_invalid_api_key(self):
        """Test event capture with invalid API key"""
        url = reverse('capture_event')
        event_data = {
            'event_name': 'test_event',
            'api_key': 'invalid_key'
        }
        
        response = self.client.post(
            url,
            json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('api_key', response_data)
        self.assertEqual(response_data['api_key'][0], 'Invalid or inactive API key')

    def test_capture_event_missing_api_key(self):
        """Test event capture without API key"""
        url = reverse('capture_event')
        event_data = {
            'event_name': 'test_event'
        }
        
        response = self.client.post(
            url,
            json.dumps(event_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('api_key', response_data)

    def test_capture_event_ip_rate_limiting(self):
        """Test IP-based rate limiting"""
        url = reverse('capture_event')
        event_data = {
            'event_name': 'rate_test',
            'api_key': self.project.api_key
        }
        
        # Mock rate limit to be very low for testing
        with patch('analytics.views.check_ip_rate_limit') as mock_rate_limit:
            # First request succeeds
            mock_rate_limit.return_value = (True, 1, 2)
            
            response = self.client.post(
                url,
                json.dumps(event_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
            
            # Second request fails (rate limited)
            mock_rate_limit.return_value = (False, 3, 2)
            
            response = self.client.post(
                url,
                json.dumps(event_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 429)
            response_data = response.json()
            
            self.assertIn('Rate limit exceeded for IP address', response_data['error'])
            self.assertEqual(response_data['current_count'], 3)
            self.assertEqual(response_data['limit'], 2)
            self.assertEqual(response_data['retry_after'], '60 seconds')

    def test_capture_event_project_rate_limiting(self):
        """Test project-based rate limiting"""
        url = reverse('capture_event')
        event_data = {
            'event_name': 'project_rate_test',
            'api_key': self.project.api_key
        }
        
        # Mock both rate limits - IP passes, project fails
        with patch('analytics.views.check_ip_rate_limit') as mock_ip_limit, \
             patch('analytics.views.check_project_rate_limit') as mock_project_limit:
            
            mock_ip_limit.return_value = (True, 1, 100)  # IP limit OK
            mock_project_limit.return_value = (False, 11, 10)  # Project limit exceeded
            
            response = self.client.post(
                url,
                json.dumps(event_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 429)
            response_data = response.json()
            
            self.assertIn('Rate limit exceeded for project', response_data['error'])
            self.assertEqual(response_data['current_count'], 11)
            self.assertEqual(response_data['limit'], 10)

    def test_capture_event_rate_limit_info_in_response(self):
        """Test that rate limit info is included in successful responses"""
        url = reverse('capture_event')
        event_data = {
            'event_name': 'rate_info_test',
            'api_key': self.project.api_key
        }
        
        with patch('analytics.views.check_ip_rate_limit') as mock_ip_limit, \
             patch('analytics.views.check_project_rate_limit') as mock_project_limit:
            
            mock_ip_limit.return_value = (True, 5, 100)
            mock_project_limit.return_value = (True, 2, 10)
            
            response = self.client.post(
                url,
                json.dumps(event_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
            response_data = response.json()
            
            rate_info = response_data['rate_limit_info']
            self.assertEqual(rate_info['ip_usage'], '5/100')
            self.assertEqual(rate_info['project_usage'], '2/10')

    def test_capture_event_source_validation(self):
        """Test source validation against project allowed_sources"""
        # Update project to only allow specific sources
        self.project.allowed_sources = ['web', 'mobile']
        self.project.save()
        
        url = reverse('capture_event')
        
        # Valid source should work
        valid_event = {
            'event_name': 'valid_source_test',
            'source': 'web',
            'api_key': self.project.api_key
        }
        
        response = self.client.post(
            url,
            json.dumps(valid_event),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Invalid source should fail
        invalid_event = {
            'event_name': 'invalid_source_test',
            'source': 'desktop',
            'api_key': self.project.api_key
        }
        
        response = self.client.post(
            url,
            json.dumps(invalid_event),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('source', response_data)

    def test_get_stats_success(self):
        """Test successful stats retrieval"""
        url = reverse('get_stats')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Check response structure
        self.assertIn('daily_stats', response_data)
        self.assertIn('event_counts', response_data)
        self.assertIn('source_counts', response_data)
        self.assertIn('recent_events', response_data)
        self.assertIn('total_events', response_data)
        
        # Check total events count
        self.assertEqual(response_data['total_events'], len(self.events_data))

    def test_get_stats_with_api_key_filter(self):
        """Test stats endpoint with API key filtering"""
        # Create another project with events
        other_project = Project.objects.create(
            name='Other Project',
            slug='other-project'
        )
        Event.objects.create(
            project=other_project,
            event_name='other_event',
            user_id='other_user',
            session_id='other_session'
        )
        
        url = reverse('get_stats')
        
        # Get stats for specific project
        response = self.client.get(url, {'api_key': self.project.api_key})
        response_data = response.json()
        
        # Should only show events from our project
        self.assertEqual(response_data['total_events'], len(self.events_data))
        
        # Get stats for other project
        response = self.client.get(url, {'api_key': other_project.api_key})
        response_data = response.json()
        
        # Should only show 1 event from other project
        self.assertEqual(response_data['total_events'], 1)

    def test_get_stats_invalid_api_key(self):
        """Test stats endpoint with invalid API key"""
        url = reverse('get_stats')
        
        response = self.client.get(url, {'api_key': 'invalid_key'})
        
        self.assertEqual(response.status_code, 401)
        response_data = response.json()
        self.assertIn('Invalid API key', response_data['error'])

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
            self.assertIn('user_id', event)
            self.assertIn('session_id', event)
            self.assertIn('project_name', event)

    def test_capture_event_user_session_generation(self):
        """Test automatic user_id and session_id generation"""
        url = reverse('capture_event')
        event_data = {
            'event_name': 'session_test',
            'api_key': self.project.api_key
        }
        
        response = self.client.post(
            url,
            json.dumps(event_data),
            content_type='application/json',
            HTTP_USER_AGENT='Mozilla/5.0 Test Browser'
        )
        
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        
        # User ID should be generated
        self.assertTrue(response_data['user_id'].startswith('anon_'))
        
        # Session ID should follow pattern: {user_id}_{date}_{random}
        session_id = response_data['session_id']
        user_id = response_data['user_id']
        
        self.assertTrue(session_id.startswith(user_id + '_'))
        
        # Should contain today's date in YYYYMMDD format
        today = timezone.now().strftime('%Y%m%d')
        self.assertIn(today, session_id)

    def test_multiple_requests_same_user_agent_consistent_user_id(self):
        """Test that same user agent gets consistent user ID"""
        url = reverse('capture_event')
        event_data = {
            'event_name': 'consistency_test',
            'api_key': self.project.api_key
        }
        
        # Make two requests with same user agent
        response1 = self.client.post(
            url,
            json.dumps({**event_data, 'event_name': 'test_1'}),
            content_type='application/json',
            HTTP_USER_AGENT='Consistent Test Browser'
        )
        
        response2 = self.client.post(
            url,
            json.dumps({**event_data, 'event_name': 'test_2'}),
            content_type='application/json',
            HTTP_USER_AGENT='Consistent Test Browser'
        )
        
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Should have same user_id
        self.assertEqual(data1['user_id'], data2['user_id'])
        
        # Should have different session_ids (different random numbers)
        self.assertNotEqual(data1['session_id'], data2['session_id'])