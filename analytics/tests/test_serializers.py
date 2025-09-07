from django.test import TestCase, RequestFactory
from unittest.mock import patch, Mock

from analytics.models import Project, Event
from analytics.serializers import EventSerializer, EventCreateSerializer


class EventSerializerTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.project = Project.objects.create(
            name='Test Project',
            slug='test-project'
        )
        self.event = Event.objects.create(
            project=self.project,
            event_name='test_event',
            source='web',
            user_id='anon_12345678',
            session_id='anon_12345678_20250907_1234',
            properties={'user_id': 123, 'source': 'test'},
            user_agent='Test Browser',
            ip_address='127.0.0.1'
        )

    def test_event_serializer_serialization(self):
        """Test EventSerializer serializes model correctly"""
        serializer = EventSerializer(self.event)
        data = serializer.data
        
        self.assertEqual(data['event_name'], 'test_event')
        self.assertEqual(data['source'], 'web')
        self.assertEqual(data['user_id'], 'anon_12345678')
        self.assertEqual(data['session_id'], 'anon_12345678_20250907_1234')
        self.assertEqual(data['properties'], {'user_id': 123, 'source': 'test'})
        self.assertEqual(data['project_name'], 'Test Project')
        self.assertEqual(data['user_agent'], 'Test Browser')
        self.assertEqual(data['ip_address'], '127.0.0.1')
        self.assertIn('id', data)
        self.assertIn('timestamp', data)


class EventCreateSerializerTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.project = Project.objects.create(
            name='Test Project',
            slug='test-project',
            allowed_sources=['web', 'mobile']
        )

    def test_event_create_serializer_valid_data(self):
        """Test EventCreateSerializer with valid data"""
        request = self.factory.post('/api/capture_event/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'Test Browser'
        
        event_data = {
            'event_name': 'serializer_test',
            'source': 'web',
            'api_key': self.project.api_key,
            'properties': {'key': 'value'}
        }
        
        serializer = EventCreateSerializer(data=event_data, context={'request': request})
        
        self.assertTrue(serializer.is_valid())
        event = serializer.save()
        
        self.assertEqual(event.event_name, 'serializer_test')
        self.assertEqual(event.source, 'web')
        self.assertEqual(event.project, self.project)
        self.assertEqual(event.properties, {'key': 'value'})
        self.assertTrue(event.user_id.startswith('anon_'))
        self.assertTrue(event.session_id.startswith('anon_'))
        self.assertEqual(event.user_agent, 'Test Browser')
        self.assertEqual(event.ip_address, '127.0.0.1')

    def test_event_create_serializer_minimal_data(self):
        """Test EventCreateSerializer with minimal required data"""
        request = self.factory.post('/api/capture_event/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        event_data = {
            'event_name': 'minimal_test',
            'api_key': self.project.api_key
        }
        
        serializer = EventCreateSerializer(data=event_data, context={'request': request})
        
        self.assertTrue(serializer.is_valid())
        event = serializer.save()
        
        self.assertEqual(event.event_name, 'minimal_test')
        self.assertEqual(event.source, 'web')  # default value
        self.assertEqual(event.properties, {})
        self.assertTrue(event.user_id)
        self.assertTrue(event.session_id)
        self.assertEqual(event.ip_address, '192.168.1.1')

    def test_event_create_serializer_invalid_api_key(self):
        """Test EventCreateSerializer with invalid API key"""
        event_data = {
            'event_name': 'invalid_key_test',
            'api_key': 'invalid_key'
        }
        
        serializer = EventCreateSerializer(data=event_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('api_key', serializer.errors)
        self.assertEqual(serializer.errors['api_key'][0], 'Invalid or inactive API key')

    def test_event_create_serializer_missing_api_key(self):
        """Test EventCreateSerializer with missing API key"""
        event_data = {
            'event_name': 'missing_key_test'
        }
        
        serializer = EventCreateSerializer(data=event_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('api_key', serializer.errors)

    def test_event_create_serializer_source_validation(self):
        """Test source validation against project allowed_sources"""
        request = self.factory.post('/api/capture_event/')
        
        # Valid source
        valid_data = {
            'event_name': 'source_test',
            'source': 'web',
            'api_key': self.project.api_key
        }
        
        serializer = EventCreateSerializer(data=valid_data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        # Invalid source
        invalid_data = {
            'event_name': 'source_test',
            'source': 'desktop',  # Not in allowed_sources
            'api_key': self.project.api_key
        }
        
        serializer = EventCreateSerializer(data=invalid_data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('source', serializer.errors)
        self.assertIn('not allowed', serializer.errors['source'][0])

    def test_event_create_serializer_inactive_project(self):
        """Test validation with inactive project"""
        # Deactivate the project
        self.project.is_active = False
        self.project.save()
        
        event_data = {
            'event_name': 'inactive_project_test',
            'api_key': self.project.api_key
        }
        
        serializer = EventCreateSerializer(data=event_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('api_key', serializer.errors)
        self.assertEqual(serializer.errors['api_key'][0], 'Invalid or inactive API key')

    def test_event_create_serializer_user_id_generation(self):
        """Test automatic user_id generation"""
        request = self.factory.post('/api/capture_event/')
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'Custom Browser/1.0'
        
        event_data = {
            'event_name': 'user_id_test',
            'api_key': self.project.api_key
        }
        
        serializer = EventCreateSerializer(data=event_data, context={'request': request})
        
        self.assertTrue(serializer.is_valid())
        event = serializer.save()
        
        # User ID should be generated from IP + User-Agent
        self.assertTrue(event.user_id.startswith('anon_'))
        self.assertEqual(len(event.user_id), 13)  # "anon_" + 8 hex chars

    def test_event_create_serializer_session_id_generation(self):
        """Test automatic session_id generation"""
        request = self.factory.post('/api/capture_event/')
        request.META['REMOTE_ADDR'] = '172.16.0.1'
        
        event_data = {
            'event_name': 'session_id_test',
            'api_key': self.project.api_key
        }
        
        with patch('analytics.utils.timezone.now') as mock_now:
            from django.utils import timezone
            mock_time = timezone.datetime(2025, 9, 7, 14, 30, 45)
            mock_now.return_value = mock_time.replace(tzinfo=timezone.utc)
            
            serializer = EventCreateSerializer(data=event_data, context={'request': request})
            
            self.assertTrue(serializer.is_valid())
            event = serializer.save()
            
            # Session ID should follow pattern: {user_id}_{date}_{random_4_digits}
            parts = event.session_id.split('_')
            self.assertEqual(len(parts), 4)  # anon, hash, date, random
            self.assertEqual(parts[2], '20250907')  # Date part
            self.assertEqual(len(parts[3]), 4)  # Random digits

    def test_event_create_serializer_provided_user_session_ids(self):
        """Test that provided user_id and session_id are used"""
        request = self.factory.post('/api/capture_event/')
        
        event_data = {
            'event_name': 'provided_ids_test',
            'api_key': self.project.api_key,
            'user_id': 'custom_user_123',
            'session_id': 'custom_session_456'
        }
        
        serializer = EventCreateSerializer(data=event_data, context={'request': request})
        
        self.assertTrue(serializer.is_valid())
        event = serializer.save()
        
        # Should use provided IDs
        self.assertEqual(event.user_id, 'custom_user_123')
        self.assertEqual(event.session_id, 'custom_session_456')

    def test_event_create_serializer_no_request_context(self):
        """Test serializer without request context (fallback behavior)"""
        event_data = {
            'event_name': 'no_context_test',
            'api_key': self.project.api_key
        }
        
        serializer = EventCreateSerializer(data=event_data)  # No context
        
        self.assertTrue(serializer.is_valid())
        event = serializer.save()
        
        # Should still generate user_id and session_id with fallback
        self.assertTrue(event.user_id.startswith('anon_'))
        self.assertTrue(event.session_id.startswith('anon_'))
        # IP and user_agent should be empty/None since no request
        self.assertIn(event.ip_address, [None, ''])
        self.assertIn(event.user_agent, [None, ''])

    def test_event_create_serializer_server_side_ip_override(self):
        """Test that server-side IP extraction overrides client data"""
        request = self.factory.post('/api/capture_event/')
        request.META['REMOTE_ADDR'] = '203.0.113.1'  # Server-detected IP
        request.META['HTTP_USER_AGENT'] = 'Server Browser'
        
        event_data = {
            'event_name': 'ip_override_test',
            'api_key': self.project.api_key,
            'ip_address': '192.168.1.100',  # Client-provided IP (should be ignored)
            'user_agent': 'Client Browser'   # Client-provided UA (should be ignored)
        }
        
        serializer = EventCreateSerializer(data=event_data, context={'request': request})
        
        self.assertTrue(serializer.is_valid())
        event = serializer.save()
        
        # Server-side values should win for security
        self.assertEqual(event.ip_address, '203.0.113.1')
        self.assertEqual(event.user_agent, 'Server Browser')