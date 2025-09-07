from django.contrib import admin
from .models import Project, Event, ProjectRateLimit, IPRateLimit


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'rate_limit_per_minute', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['api_key', 'secret_key', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'is_active')
        }),
        ('Authentication', {
            'fields': ('api_key', 'secret_key'),
            'classes': ('collapse',),
        }),
        ('Configuration', {
            'fields': ('allowed_sources', 'rate_limit_per_minute'),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event_name', 'source', 'project', 'timestamp', 'ip_address']
    list_filter = ['project', 'source', 'event_name', 'timestamp']
    search_fields = ['event_name', 'source', 'properties']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')


@admin.register(ProjectRateLimit)
class ProjectRateLimitAdmin(admin.ModelAdmin):
    list_display = ['project', 'minute_bucket', 'request_count']
    list_filter = ['project', 'minute_bucket']
    readonly_fields = ['minute_bucket', 'request_count']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')


@admin.register(IPRateLimit)
class IPRateLimitAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'minute_bucket', 'request_count']
    list_filter = ['minute_bucket', 'request_count']
    search_fields = ['ip_address']
    readonly_fields = ['minute_bucket', 'request_count']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-minute_bucket', '-request_count')