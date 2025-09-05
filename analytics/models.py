from django.db import models
from django.utils import timezone

class Event(models.Model):
    event_name = models.CharField(max_length=100)
    source = models.CharField(max_length=50, default='web', help_text='Source application or system')
    timestamp = models.DateTimeField(default=timezone.now)
    properties = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['source', 'event_name']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.source}.{self.event_name} at {self.timestamp}"