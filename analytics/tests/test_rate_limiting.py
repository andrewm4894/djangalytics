from django.test import TestCase, RequestFactory
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, Mock

from analytics.models import Project, IPRateLimit, ProjectRateLimit
from analytics.utils import (
    check_ip_rate_limit, 
    check_project_rate_limit, 
    get_current_minute_bucket,
    cleanup_old_rate_limits
)


class RateLimitUtilsTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.project = Project.objects.create(
            name='Test Project',
            slug='test-project',
            rate_limit_per_minute=10
        )

    def test_get_current_minute_bucket(self):
        """Test minute bucket calculation"""
        with patch('django.utils.timezone.now') as mock_now:
            # Mock a specific time
            mock_time = timezone.datetime(2025, 9, 7, 14, 30, 45, 123456)
            mock_now.return_value = mock_time.replace(tzinfo=timezone.utc)
            
            bucket = get_current_minute_bucket()
            expected = mock_time.replace(second=0, microsecond=0, tzinfo=timezone.utc)
            
            self.assertEqual(bucket, expected)

    def test_check_ip_rate_limit_first_request(self):
        """Test IP rate limiting on first request"""
        request = self.factory.post('/api/capture_event/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        is_allowed, count, limit = check_ip_rate_limit(request, limit_per_minute=5)
        
        self.assertTrue(is_allowed)
        self.assertEqual(count, 1)
        self.assertEqual(limit, 5)
        
        # Verify database record was created
        self.assertEqual(IPRateLimit.objects.count(), 1)
        rate_limit = IPRateLimit.objects.first()
        self.assertEqual(rate_limit.ip_address, '127.0.0.1')
        self.assertEqual(rate_limit.request_count, 1)

    def test_check_ip_rate_limit_multiple_requests(self):
        """Test IP rate limiting with multiple requests"""
        request = self.factory.post('/api/capture_event/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        # Make 3 requests
        for i in range(3):
            is_allowed, count, limit = check_ip_rate_limit(request, limit_per_minute=5)
            self.assertTrue(is_allowed)
            self.assertEqual(count, i + 1)
            self.assertEqual(limit, 5)
        
        # Should still be only 1 database record
        self.assertEqual(IPRateLimit.objects.count(), 1)
        rate_limit = IPRateLimit.objects.first()
        self.assertEqual(rate_limit.request_count, 3)

    def test_check_ip_rate_limit_exceeded(self):
        """Test IP rate limiting when limit is exceeded"""
        request = self.factory.post('/api/capture_event/')
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        
        # Make requests up to the limit
        for i in range(3):
            is_allowed, count, limit = check_ip_rate_limit(request, limit_per_minute=3)
            self.assertTrue(is_allowed)
            self.assertEqual(count, i + 1)
        
        # Next request should be rate limited
        is_allowed, count, limit = check_ip_rate_limit(request, limit_per_minute=3)
        self.assertFalse(is_allowed)
        self.assertEqual(count, 4)  # Still increments
        self.assertEqual(limit, 3)

    def test_check_ip_rate_limit_different_ips(self):
        """Test that different IPs have separate rate limits"""
        request1 = self.factory.post('/api/capture_event/')
        request1.META['REMOTE_ADDR'] = '1.1.1.1'
        
        request2 = self.factory.post('/api/capture_event/')
        request2.META['REMOTE_ADDR'] = '2.2.2.2'
        
        # Each IP should have its own counter
        is_allowed1, count1, _ = check_ip_rate_limit(request1, limit_per_minute=2)
        is_allowed2, count2, _ = check_ip_rate_limit(request2, limit_per_minute=2)
        
        self.assertTrue(is_allowed1)
        self.assertTrue(is_allowed2)
        self.assertEqual(count1, 1)
        self.assertEqual(count2, 1)
        
        # Should have 2 separate database records
        self.assertEqual(IPRateLimit.objects.count(), 2)

    def test_check_project_rate_limit_first_request(self):
        """Test project rate limiting on first request"""
        is_allowed, count, limit = check_project_rate_limit(self.project)
        
        self.assertTrue(is_allowed)
        self.assertEqual(count, 1)
        self.assertEqual(limit, 10)  # From project setup
        
        # Verify database record was created
        self.assertEqual(ProjectRateLimit.objects.count(), 1)
        rate_limit = ProjectRateLimit.objects.first()
        self.assertEqual(rate_limit.project, self.project)
        self.assertEqual(rate_limit.request_count, 1)

    def test_check_project_rate_limit_custom_limit(self):
        """Test project rate limiting with custom limit override"""
        is_allowed, count, limit = check_project_rate_limit(self.project, limit_per_minute=5)
        
        self.assertTrue(is_allowed)
        self.assertEqual(count, 1)
        self.assertEqual(limit, 5)  # Override limit

    def test_check_project_rate_limit_exceeded(self):
        """Test project rate limiting when limit is exceeded"""
        # Make requests up to the limit
        for i in range(2):
            is_allowed, count, limit = check_project_rate_limit(self.project, limit_per_minute=2)
            self.assertTrue(is_allowed)
            self.assertEqual(count, i + 1)
        
        # Next request should be rate limited
        is_allowed, count, limit = check_project_rate_limit(self.project, limit_per_minute=2)
        self.assertFalse(is_allowed)
        self.assertEqual(count, 3)  # Still increments
        self.assertEqual(limit, 2)

    def test_cleanup_old_rate_limits(self):
        """Test cleanup of old rate limit records"""
        current_time = timezone.now()
        old_time = current_time - timedelta(days=10)
        
        # Create some old records
        IPRateLimit.objects.create(
            ip_address='127.0.0.1',
            minute_bucket=old_time,
            request_count=5
        )
        ProjectRateLimit.objects.create(
            project=self.project,
            minute_bucket=old_time,
            request_count=3
        )
        
        # Create some recent records
        recent_time = current_time - timedelta(days=1)
        IPRateLimit.objects.create(
            ip_address='127.0.0.1',
            minute_bucket=recent_time,
            request_count=2
        )
        ProjectRateLimit.objects.create(
            project=self.project,
            minute_bucket=recent_time,
            request_count=1
        )
        
        # Verify we have 4 records total
        self.assertEqual(IPRateLimit.objects.count(), 2)
        self.assertEqual(ProjectRateLimit.objects.count(), 2)
        
        # Clean up old records (keep 7 days)
        ip_deleted, project_deleted = cleanup_old_rate_limits(days_to_keep=7)
        
        # Should have deleted 1 of each type
        self.assertEqual(ip_deleted, 1)
        self.assertEqual(project_deleted, 1)
        
        # Should have 1 recent record of each type remaining
        self.assertEqual(IPRateLimit.objects.count(), 1)
        self.assertEqual(ProjectRateLimit.objects.count(), 1)
        
        # Verify the remaining records are recent
        remaining_ip = IPRateLimit.objects.first()
        remaining_project = ProjectRateLimit.objects.first()
        self.assertEqual(remaining_ip.minute_bucket, recent_time)
        self.assertEqual(remaining_project.minute_bucket, recent_time)

    def test_rate_limiting_across_different_minutes(self):
        """Test that rate limits reset for different minute buckets"""
        request = self.factory.post('/api/capture_event/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # Mock the first minute
        with patch('analytics.utils.get_current_minute_bucket') as mock_bucket:
            minute1 = timezone.now().replace(second=0, microsecond=0)
            mock_bucket.return_value = minute1
            
            # Use up the rate limit for minute 1
            for i in range(2):
                is_allowed, count, limit = check_ip_rate_limit(request, limit_per_minute=2)
                self.assertTrue(is_allowed)
            
            # Should be rate limited now
            is_allowed, count, limit = check_ip_rate_limit(request, limit_per_minute=2)
            self.assertFalse(is_allowed)
            self.assertEqual(count, 3)
        
        # Mock the next minute
        with patch('analytics.utils.get_current_minute_bucket') as mock_bucket:
            minute2 = minute1 + timedelta(minutes=1)
            mock_bucket.return_value = minute2
            
            # Should be allowed again in new minute
            is_allowed, count, limit = check_ip_rate_limit(request, limit_per_minute=2)
            self.assertTrue(is_allowed)
            self.assertEqual(count, 1)  # Reset for new minute
        
        # Should have 2 database records (one for each minute)
        self.assertEqual(IPRateLimit.objects.count(), 2)