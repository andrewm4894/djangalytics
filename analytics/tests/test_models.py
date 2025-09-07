from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from analytics.models import Project, Event, IPRateLimit, ProjectRateLimit


class ProjectModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.project_data = {
            'name': 'Test Project',
            'slug': 'test-project',
            'allowed_sources': ['web', 'mobile'],
            'rate_limit_per_minute': 500
        }

    def test_project_creation(self):
        """Test creating a project with all fields"""
        project = Project.objects.create(**self.project_data)
        
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.slug, 'test-project')
        self.assertEqual(project.allowed_sources, ['web', 'mobile'])
        self.assertEqual(project.rate_limit_per_minute, 500)
        self.assertTrue(project.is_active)
        self.assertIsInstance(project.created_at, datetime)
        self.assertTrue(project.id)

    def test_project_api_keys_generated(self):
        """Test that API keys are automatically generated"""
        project = Project.objects.create(name='Test', slug='test')
        
        self.assertTrue(project.api_key.startswith('pk_'))
        self.assertTrue(project.secret_key.startswith('sk_'))
        self.assertEqual(len(project.api_key), 3 + 43)  # "pk_" + 43 chars
        self.assertEqual(len(project.secret_key), 3 + 43)  # "sk_" + 43 chars

    def test_project_is_source_allowed_empty_list(self):
        """Test that empty allowed_sources allows all sources"""
        project = Project.objects.create(
            name='Test', 
            slug='test',
            allowed_sources=[]
        )
        
        self.assertTrue(project.is_source_allowed('web'))
        self.assertTrue(project.is_source_allowed('mobile'))
        self.assertTrue(project.is_source_allowed('anything'))

    def test_project_is_source_allowed_with_restrictions(self):
        """Test source validation with restricted list"""
        project = Project.objects.create(
            name='Test', 
            slug='test',
            allowed_sources=['web', 'mobile']
        )
        
        self.assertTrue(project.is_source_allowed('web'))
        self.assertTrue(project.is_source_allowed('mobile'))
        self.assertFalse(project.is_source_allowed('desktop'))
        self.assertFalse(project.is_source_allowed('api'))

    def test_project_str_representation(self):
        """Test the string representation of Project"""
        project = Project.objects.create(name='Test Project', slug='test')
        self.assertEqual(str(project), 'Test Project')


class EventModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.project = Project.objects.create(
            name='Test Project',
            slug='test-project'
        )
        self.event_data = {
            'project': self.project,
            'event_name': 'test_event',
            'source': 'web',
            'properties': {'user_id': 123, 'source': 'test'},
            'user_id': 'anon_12345678',
            'session_id': 'anon_12345678_20250907_1234'
        }

    def test_event_creation(self):
        """Test creating an event with all fields"""
        event = Event.objects.create(**self.event_data)
        
        self.assertEqual(event.event_name, 'test_event')
        self.assertEqual(event.source, 'web')
        self.assertEqual(event.properties, {'user_id': 123, 'source': 'test'})
        self.assertEqual(event.user_id, 'anon_12345678')
        self.assertEqual(event.session_id, 'anon_12345678_20250907_1234')
        self.assertEqual(event.project, self.project)
        self.assertIsInstance(event.timestamp, datetime)
        self.assertTrue(event.id)

    def test_event_creation_minimal(self):
        """Test creating an event with only required fields"""
        event = Event.objects.create(
            project=self.project,
            event_name='minimal_event'
        )
        
        self.assertEqual(event.event_name, 'minimal_event')
        self.assertEqual(event.source, 'web')  # default
        self.assertEqual(event.properties, {})
        self.assertIsInstance(event.timestamp, datetime)

    def test_event_str_representation(self):
        """Test the string representation of Event"""
        event = Event.objects.create(**self.event_data)
        expected_str = f"Test Project.web.test_event at {event.timestamp}"
        self.assertEqual(str(event), expected_str)

    def test_event_ordering(self):
        """Test that events are ordered by timestamp descending"""
        old_event = Event.objects.create(
            project=self.project,
            event_name='old_event',
            timestamp=timezone.now() - timedelta(hours=1)
        )
        new_event = Event.objects.create(
            project=self.project,
            event_name='new_event',
            timestamp=timezone.now()
        )
        
        events = Event.objects.all()
        self.assertEqual(events[0], new_event)  # Most recent first
        self.assertEqual(events[1], old_event)


class RateLimitModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.project = Project.objects.create(
            name='Test Project',
            slug='test-project'
        )
        self.minute_bucket = timezone.now().replace(second=0, microsecond=0)

    def test_project_rate_limit_creation(self):
        """Test creating a project rate limit record"""
        rate_limit = ProjectRateLimit.objects.create(
            project=self.project,
            minute_bucket=self.minute_bucket,
            request_count=5
        )
        
        self.assertEqual(rate_limit.project, self.project)
        self.assertEqual(rate_limit.minute_bucket, self.minute_bucket)
        self.assertEqual(rate_limit.request_count, 5)

    def test_project_rate_limit_str(self):
        """Test string representation of ProjectRateLimit"""
        rate_limit = ProjectRateLimit.objects.create(
            project=self.project,
            minute_bucket=self.minute_bucket,
            request_count=10
        )
        
        expected_str = f"Test Project - {self.minute_bucket}: 10 requests"
        self.assertEqual(str(rate_limit), expected_str)

    def test_ip_rate_limit_creation(self):
        """Test creating an IP rate limit record"""
        rate_limit = IPRateLimit.objects.create(
            ip_address='127.0.0.1',
            minute_bucket=self.minute_bucket,
            request_count=15
        )
        
        self.assertEqual(rate_limit.ip_address, '127.0.0.1')
        self.assertEqual(rate_limit.minute_bucket, self.minute_bucket)
        self.assertEqual(rate_limit.request_count, 15)

    def test_ip_rate_limit_str(self):
        """Test string representation of IPRateLimit"""
        rate_limit = IPRateLimit.objects.create(
            ip_address='192.168.1.1',
            minute_bucket=self.minute_bucket,
            request_count=25
        )
        
        expected_str = f"192.168.1.1 - {self.minute_bucket}: 25 requests"
        self.assertEqual(str(rate_limit), expected_str)

    def test_unique_constraints(self):
        """Test unique constraints on rate limit models"""
        # Create first rate limit
        ProjectRateLimit.objects.create(
            project=self.project,
            minute_bucket=self.minute_bucket,
            request_count=1
        )
        
        # Try to create duplicate - should raise IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ProjectRateLimit.objects.create(
                project=self.project,
                minute_bucket=self.minute_bucket,
                request_count=2
            )
        
        # Same for IP rate limits
        IPRateLimit.objects.create(
            ip_address='127.0.0.1',
            minute_bucket=self.minute_bucket,
            request_count=1
        )
        
        with self.assertRaises(IntegrityError):
            IPRateLimit.objects.create(
                ip_address='127.0.0.1',
                minute_bucket=self.minute_bucket,
                request_count=2
            )