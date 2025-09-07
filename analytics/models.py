from django.db import models
from django.utils import timezone
import uuid
import secrets


class Project(models.Model):
    """
    Represents a project/application that sends analytics events.
    Each project has a unique API key for authentication.
    """
    name = models.CharField(max_length=100, help_text='Human-readable project name')
    slug = models.SlugField(unique=True, help_text='URL-friendly identifier')
    
    # Authentication
    api_key = models.CharField(max_length=64, unique=True, help_text='Public API key')
    secret_key = models.CharField(max_length=64, unique=True, help_text='Secret key (optional, for server-side)')
    
    # Configuration
    allowed_sources = models.JSONField(
        default=list, 
        blank=True,
        help_text='List of allowed source names (empty = allow all)'
    )
    rate_limit_per_minute = models.IntegerField(
        default=1000,
        help_text='Maximum events per minute'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['api_key']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Generate API keys if not provided
        if not self.api_key:
            self.api_key = f"pk_{secrets.token_urlsafe(32)}"
        if not self.secret_key:
            self.secret_key = f"sk_{secrets.token_urlsafe(32)}"
        super().save(*args, **kwargs)
    
    def is_source_allowed(self, source):
        """Check if a source is allowed for this project."""
        if not self.allowed_sources:  # Empty list means allow all
            return True
        return source in self.allowed_sources


class Event(models.Model):
    """
    Analytics event with required project association.
    """
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='events',
        help_text='Project that sent this event'
    )
    event_name = models.CharField(max_length=100)
    source = models.CharField(max_length=50, default='web', help_text='Source application or system')
    timestamp = models.DateTimeField(default=timezone.now)
    properties = models.JSONField(default=dict, blank=True)
    
    # User and session tracking
    user_id = models.CharField(
        max_length=64, 
        null=True, 
        blank=True, 
        help_text='User identifier (anonymous cookie-based or authenticated)'
    )
    session_id = models.CharField(
        max_length=64, 
        null=True, 
        blank=True, 
        help_text='Session identifier (auto-generated: user_id_date_random)'
    )
    
    # Analytics metadata
    user_agent = models.TextField(blank=True, help_text='Browser/client user agent')
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text='Client IP address')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['project', 'source', 'event_name']),
            models.Index(fields=['project', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user_id']),
            models.Index(fields=['session_id']),
            models.Index(fields=['project', 'user_id']),
            models.Index(fields=['project', 'session_id']),
        ]
    
    def __str__(self):
        return f"{self.project.name}.{self.source}.{self.event_name} at {self.timestamp}"


class ProjectRateLimit(models.Model):
    """
    Rate limiting tracking for projects.
    Tracks request counts per minute for rate limiting.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    minute_bucket = models.DateTimeField(help_text='Minute bucket (rounded down)')
    request_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['project', 'minute_bucket']
        indexes = [
            models.Index(fields=['project', 'minute_bucket']),
        ]
    
    def __str__(self):
        return f"{self.project.name} - {self.minute_bucket}: {self.request_count} requests"


class IPRateLimit(models.Model):
    """
    Rate limiting tracking for IP addresses.
    Prevents abuse from individual IPs regardless of project.
    """
    ip_address = models.GenericIPAddressField(help_text='Client IP address')
    minute_bucket = models.DateTimeField(help_text='Minute bucket (rounded down)')
    request_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['ip_address', 'minute_bucket']
        indexes = [
            models.Index(fields=['ip_address', 'minute_bucket']),
            models.Index(fields=['minute_bucket']),  # For cleanup queries
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.minute_bucket}: {self.request_count} requests"