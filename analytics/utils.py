import hashlib
import secrets
import uuid
from datetime import datetime
from django.utils import timezone


def generate_anonymous_user_id(request=None, fallback_data=None):
    """
    Generate a consistent anonymous user ID based on available data.
    
    Priority:
    1. Use existing cookie if available
    2. Generate from IP + User-Agent hash for consistency
    3. Use fallback data if provided
    4. Generate random UUID as last resort
    
    Args:
        request: Django request object (optional)
        fallback_data: Dict with 'ip_address', 'user_agent' (optional)
    
    Returns:
        str: Anonymous user ID (format: anon_[8_chars])
    """
    # Try to get data from request
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    elif fallback_data:
        ip_address = fallback_data.get('ip_address')
        user_agent = fallback_data.get('user_agent', '')
    
    # Generate consistent ID from IP + User-Agent if available
    if ip_address and user_agent:
        # Create hash from IP + User-Agent for consistent anonymous ID
        hash_input = f"{ip_address}:{user_agent}".encode('utf-8')
        hash_digest = hashlib.sha256(hash_input).hexdigest()[:8]
        return f"anon_{hash_digest}"
    
    # Fallback to random UUID
    return f"anon_{uuid.uuid4().hex[:8]}"


def generate_session_id(user_id, existing_session_id=None):
    """
    Generate session ID using pattern: {user_id}_{date}_{random_4_digits}
    
    Args:
        user_id: User identifier
        existing_session_id: Return this if already provided
        
    Returns:
        str: Session ID
    """
    if existing_session_id:
        return existing_session_id
        
    if not user_id:
        user_id = "unknown"
    
    # Get today's date in YYYYMMDD format
    today = timezone.now().strftime('%Y%m%d')
    
    # Generate 4 random digits
    random_digits = secrets.randbelow(10000)  # 0-9999
    
    return f"{user_id}_{today}_{random_digits:04d}"


def get_client_ip(request):
    """
    Extract client IP address from request, handling proxies.
    
    Args:
        request: Django request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP in the chain (original client)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def parse_user_agent(user_agent_string):
    """
    Parse user agent string for basic browser/device info.
    
    Args:
        user_agent_string: Raw user agent string
        
    Returns:
        dict: Parsed information
    """
    if not user_agent_string:
        return {}
    
    info = {
        'browser': 'Unknown',
        'os': 'Unknown', 
        'device': 'Desktop'
    }
    
    ua_lower = user_agent_string.lower()
    
    # Basic browser detection
    if 'chrome' in ua_lower and 'edg' not in ua_lower:
        info['browser'] = 'Chrome'
    elif 'firefox' in ua_lower:
        info['browser'] = 'Firefox'
    elif 'safari' in ua_lower and 'chrome' not in ua_lower:
        info['browser'] = 'Safari'
    elif 'edg' in ua_lower:
        info['browser'] = 'Edge'
    
    # Basic OS detection
    if 'windows' in ua_lower:
        info['os'] = 'Windows'
    elif 'mac' in ua_lower:
        info['os'] = 'macOS'
    elif 'linux' in ua_lower:
        info['os'] = 'Linux'
    elif 'android' in ua_lower:
        info['os'] = 'Android'
        info['device'] = 'Mobile'
    elif 'iphone' in ua_lower or 'ipad' in ua_lower:
        info['os'] = 'iOS'
        info['device'] = 'Mobile' if 'iphone' in ua_lower else 'Tablet'
    
    return info


def should_sample_event(event_name, sample_rate=0.1):
    """
    Determine if an event should be sampled (for high-frequency events).
    
    Args:
        event_name: Name of the event
        sample_rate: Sampling rate (0.0 to 1.0)
        
    Returns:
        bool: True if event should be recorded
    """
    # High-frequency events that should be sampled
    high_frequency_events = {
        'direction_changed', 
        'hedgehog_flap',
        'mouse_move',
        'scroll',
        'key_press'
    }
    
    if event_name in high_frequency_events:
        return secrets.randbelow(100) < (sample_rate * 100)
    
    # Always record other events
    return True


def get_current_minute_bucket():
    """
    Get the current minute bucket for rate limiting (rounded down to the minute).
    
    Returns:
        datetime: Current time rounded down to the minute
    """
    now = timezone.now()
    return now.replace(second=0, microsecond=0)


def check_ip_rate_limit(request, limit_per_minute=100):
    """
    Check if an IP address is within rate limits.
    
    Args:
        request: Django request object
        limit_per_minute: Maximum requests per minute per IP
        
    Returns:
        tuple: (is_allowed: bool, current_count: int, limit: int)
    """
    from .models import IPRateLimit
    from django.db import transaction
    
    ip_address = get_client_ip(request)
    minute_bucket = get_current_minute_bucket()
    
    with transaction.atomic():
        # Get or create rate limit record for this IP and minute
        rate_limit, created = IPRateLimit.objects.get_or_create(
            ip_address=ip_address,
            minute_bucket=minute_bucket,
            defaults={'request_count': 1}
        )
        
        if not created:
            # Atomically increment the count using F() expression
            from django.db.models import F
            IPRateLimit.objects.filter(
                ip_address=ip_address,
                minute_bucket=minute_bucket
            ).update(request_count=F('request_count') + 1)
            
            # Refresh the object to get the updated count
            rate_limit.refresh_from_db()
        
        # Check if over limit
        is_allowed = rate_limit.request_count <= limit_per_minute
        
        return is_allowed, rate_limit.request_count, limit_per_minute


def check_project_rate_limit(project, limit_per_minute=None):
    """
    Check if a project is within rate limits.
    
    Args:
        project: Project model instance
        limit_per_minute: Override limit (uses project limit if None)
        
    Returns:
        tuple: (is_allowed: bool, current_count: int, limit: int)
    """
    from .models import ProjectRateLimit
    from django.db import transaction
    
    if limit_per_minute is None:
        limit_per_minute = project.rate_limit_per_minute
    
    minute_bucket = get_current_minute_bucket()
    
    with transaction.atomic():
        # Get or create rate limit record for this project and minute
        rate_limit, created = ProjectRateLimit.objects.get_or_create(
            project=project,
            minute_bucket=minute_bucket,
            defaults={'request_count': 1}
        )
        
        if not created:
            # Atomically increment the count using F() expression
            from django.db.models import F
            ProjectRateLimit.objects.filter(
                project=project,
                minute_bucket=minute_bucket
            ).update(request_count=F('request_count') + 1)
            
            # Refresh the object to get the updated count
            rate_limit.refresh_from_db()
        
        # Check if over limit
        is_allowed = rate_limit.request_count <= limit_per_minute
        
        return is_allowed, rate_limit.request_count, limit_per_minute


def cleanup_old_rate_limits(days_to_keep=7):
    """
    Clean up old rate limit records to prevent database bloat.
    
    Args:
        days_to_keep: Number of days to keep rate limit records
        
    Returns:
        tuple: (ip_records_deleted, project_records_deleted)
    """
    from .models import IPRateLimit, ProjectRateLimit
    from datetime import timedelta
    
    cutoff_time = timezone.now() - timedelta(days=days_to_keep)
    
    ip_deleted = IPRateLimit.objects.filter(minute_bucket__lt=cutoff_time).delete()[0]
    project_deleted = ProjectRateLimit.objects.filter(minute_bucket__lt=cutoff_time).delete()[0]
    
    return ip_deleted, project_deleted