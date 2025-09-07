from django.test import TestCase, RequestFactory
from unittest.mock import patch

from analytics.utils import (
    generate_anonymous_user_id,
    generate_session_id,
    get_client_ip,
    parse_user_agent,
    should_sample_event
)


class UtilsTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()

    def test_generate_anonymous_user_id_from_request(self):
        """Test user ID generation from request data"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 Test Browser'
        
        user_id = generate_anonymous_user_id(request)
        
        self.assertTrue(user_id.startswith('anon_'))
        self.assertEqual(len(user_id), 13)  # "anon_" + 8 hex chars
        
        # Should be consistent for same data
        user_id2 = generate_anonymous_user_id(request)
        self.assertEqual(user_id, user_id2)

    def test_generate_anonymous_user_id_from_fallback_data(self):
        """Test user ID generation from fallback data"""
        fallback_data = {
            'ip_address': '10.0.0.1',
            'user_agent': 'Custom Browser'
        }
        
        user_id = generate_anonymous_user_id(fallback_data=fallback_data)
        
        self.assertTrue(user_id.startswith('anon_'))
        # Should be consistent for same fallback data
        user_id2 = generate_anonymous_user_id(fallback_data=fallback_data)
        self.assertEqual(user_id, user_id2)

    def test_generate_anonymous_user_id_random_fallback(self):
        """Test user ID generation with random fallback"""
        user_id = generate_anonymous_user_id()
        
        self.assertTrue(user_id.startswith('anon_'))
        
        # Should be different each time (random)
        user_id2 = generate_anonymous_user_id()
        self.assertNotEqual(user_id, user_id2)

    def test_generate_anonymous_user_id_different_data_different_id(self):
        """Test that different IP/UA combinations give different user IDs"""
        request1 = self.factory.get('/')
        request1.META['REMOTE_ADDR'] = '1.1.1.1'
        request1.META['HTTP_USER_AGENT'] = 'Browser A'
        
        request2 = self.factory.get('/')
        request2.META['REMOTE_ADDR'] = '2.2.2.2'
        request2.META['HTTP_USER_AGENT'] = 'Browser B'
        
        user_id1 = generate_anonymous_user_id(request1)
        user_id2 = generate_anonymous_user_id(request2)
        
        self.assertNotEqual(user_id1, user_id2)

    def test_generate_session_id_pattern(self):
        """Test session ID generation follows correct pattern"""
        user_id = 'anon_12345678'
        
        with patch('analytics.utils.timezone.now') as mock_now:
            from django.utils import timezone
            mock_time = timezone.datetime(2025, 9, 7, 14, 30, 45)
            mock_now.return_value = mock_time.replace(tzinfo=timezone.utc)
            
            session_id = generate_session_id(user_id)
            
            # Should follow pattern: {user_id}_{date}_{random_4_digits}
            parts = session_id.split('_')
            self.assertEqual(len(parts), 4)
            self.assertEqual('_'.join(parts[:3]), 'anon_12345678_20250907')
            self.assertEqual(len(parts[3]), 4)  # 4-digit random number
            self.assertTrue(parts[3].isdigit())

    def test_generate_session_id_existing_session(self):
        """Test that existing session ID is returned unchanged"""
        existing_session = 'existing_session_123'
        
        result = generate_session_id('user_123', existing_session)
        
        self.assertEqual(result, existing_session)

    def test_generate_session_id_no_user_id(self):
        """Test session ID generation with no user ID"""
        session_id = generate_session_id(None)
        
        self.assertTrue(session_id.startswith('unknown_'))

    def test_get_client_ip_direct(self):
        """Test getting client IP from direct connection"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '203.0.113.1'
        
        ip = get_client_ip(request)
        
        self.assertEqual(ip, '203.0.113.1')

    def test_get_client_ip_forwarded(self):
        """Test getting client IP from X-Forwarded-For header"""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.2, 10.0.0.1, 192.168.1.1'
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        
        ip = get_client_ip(request)
        
        # Should get first IP from X-Forwarded-For
        self.assertEqual(ip, '203.0.113.2')

    def test_get_client_ip_forwarded_single(self):
        """Test getting client IP from single X-Forwarded-For entry"""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '198.51.100.1'
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        
        ip = get_client_ip(request)
        
        self.assertEqual(ip, '198.51.100.1')

    def test_parse_user_agent_chrome(self):
        """Test parsing Chrome user agent"""
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        info = parse_user_agent(ua)
        
        self.assertEqual(info['browser'], 'Chrome')
        self.assertEqual(info['os'], 'Windows')
        self.assertEqual(info['device'], 'Desktop')

    def test_parse_user_agent_firefox(self):
        """Test parsing Firefox user agent"""
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        
        info = parse_user_agent(ua)
        
        self.assertEqual(info['browser'], 'Firefox')
        self.assertEqual(info['os'], 'macOS')
        self.assertEqual(info['device'], 'Desktop')

    def test_parse_user_agent_safari(self):
        """Test parsing Safari user agent"""
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        
        info = parse_user_agent(ua)
        
        self.assertEqual(info['browser'], 'Safari')
        self.assertEqual(info['os'], 'macOS')
        self.assertEqual(info['device'], 'Desktop')

    def test_parse_user_agent_edge(self):
        """Test parsing Edge user agent"""
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        
        info = parse_user_agent(ua)
        
        self.assertEqual(info['browser'], 'Edge')
        self.assertEqual(info['os'], 'Windows')
        self.assertEqual(info['device'], 'Desktop')

    def test_parse_user_agent_mobile_android(self):
        """Test parsing Android mobile user agent"""
        ua = 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
        
        info = parse_user_agent(ua)
        
        self.assertEqual(info['browser'], 'Chrome')
        self.assertEqual(info['os'], 'Android')
        self.assertEqual(info['device'], 'Mobile')

    def test_parse_user_agent_iphone(self):
        """Test parsing iPhone user agent"""
        ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
        
        info = parse_user_agent(ua)
        
        self.assertEqual(info['browser'], 'Safari')
        self.assertEqual(info['os'], 'iOS')
        self.assertEqual(info['device'], 'Mobile')

    def test_parse_user_agent_ipad(self):
        """Test parsing iPad user agent"""
        ua = 'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
        
        info = parse_user_agent(ua)
        
        self.assertEqual(info['browser'], 'Safari')
        self.assertEqual(info['os'], 'iOS')
        self.assertEqual(info['device'], 'Tablet')

    def test_parse_user_agent_empty(self):
        """Test parsing empty user agent"""
        info = parse_user_agent('')
        
        self.assertEqual(info, {})

    def test_parse_user_agent_unknown(self):
        """Test parsing unknown user agent"""
        ua = 'RandomBot/1.0'
        
        info = parse_user_agent(ua)
        
        self.assertEqual(info['browser'], 'Unknown')
        self.assertEqual(info['os'], 'Unknown')
        self.assertEqual(info['device'], 'Desktop')

    def test_should_sample_event_high_frequency(self):
        """Test sampling for high-frequency events"""
        # Mock random to always return low value (should sample)
        with patch('analytics.utils.secrets.randbelow', return_value=5):
            result = should_sample_event('hedgehog_flap', sample_rate=0.1)
            self.assertTrue(result)  # 5 < (0.1 * 100)
        
        # Mock random to return high value (should not sample)
        with patch('analytics.utils.secrets.randbelow', return_value=15):
            result = should_sample_event('hedgehog_flap', sample_rate=0.1)
            self.assertFalse(result)  # 15 >= (0.1 * 100)

    def test_should_sample_event_regular_events(self):
        """Test that regular events are always sampled"""
        result = should_sample_event('user_signup', sample_rate=0.01)
        self.assertTrue(result)  # Regular events always recorded
        
        result = should_sample_event('page_view', sample_rate=0.0)
        self.assertTrue(result)  # Even with 0% rate, regular events recorded

    def test_should_sample_event_custom_rate(self):
        """Test sampling with custom rate"""
        # Mock to test edge cases
        with patch('analytics.utils.secrets.randbelow', return_value=50):
            # 50% sample rate
            result = should_sample_event('direction_changed', sample_rate=0.5)
            self.assertFalse(result)  # 50 >= (0.5 * 100)
            
            # 60% sample rate  
            result = should_sample_event('direction_changed', sample_rate=0.6)
            self.assertTrue(result)  # 50 < (0.6 * 100)