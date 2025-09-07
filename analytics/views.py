from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from .models import Event, Project
from .serializers import EventCreateSerializer, EventSerializer, ProjectSerializer
from .utils import check_ip_rate_limit, check_project_rate_limit

@api_view(['POST'])
def capture_event(request):
    # Check IP-based rate limiting first (100 requests per minute per IP)
    ip_allowed, ip_count, ip_limit = check_ip_rate_limit(request, limit_per_minute=100)
    if not ip_allowed:
        return Response({
            'error': 'Rate limit exceeded for IP address',
            'current_count': ip_count,
            'limit': ip_limit,
            'retry_after': '60 seconds'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Validate the event data
    serializer = EventCreateSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Get the project for project-based rate limiting
    api_key = request.data.get('api_key')
    try:
        project = Project.objects.get(api_key=api_key, is_active=True)
    except Project.DoesNotExist:
        return Response({'error': 'Invalid API key'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check project-based rate limiting
    project_allowed, project_count, project_limit = check_project_rate_limit(project)
    if not project_allowed:
        return Response({
            'error': f'Rate limit exceeded for project {project.name}',
            'current_count': project_count,
            'limit': project_limit,
            'retry_after': '60 seconds'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Save the event
    event = serializer.save()
    
    return Response({
        'id': event.id,
        'event_name': event.event_name,
        'timestamp': event.timestamp,
        'user_id': event.user_id,
        'session_id': event.session_id,
        'ip_address': event.ip_address,
        'user_agent': event.user_agent[:100] + '...' if len(event.user_agent) > 100 else event.user_agent,
        'rate_limit_info': {
            'ip_usage': f'{ip_count}/{ip_limit}',
            'project_usage': f'{project_count}/{project_limit}'
        },
        'message': 'Event captured successfully'
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_stats(request):
    # Optional project filtering via API key
    api_key = request.GET.get('api_key')
    queryset = Event.objects.all()
    
    if api_key:
        try:
            project = Project.objects.get(api_key=api_key, is_active=True)
            queryset = queryset.filter(project=project)
        except Project.DoesNotExist:
            return Response({'error': 'Invalid API key'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Parse time window and frequency parameters
    time_window = request.GET.get('time_window', '24h')  # Default 24 hours
    freq = request.GET.get('freq', '5m')   # Default 5 minutes
    
    # Parse time window to get start time
    time_window_mapping = {
        '1h': timedelta(hours=1),
        '6h': timedelta(hours=6),
        '24h': timedelta(hours=24),
        '7d': timedelta(days=7),
        '30d': timedelta(days=30)
    }
    
    window_delta = time_window_mapping.get(time_window, timedelta(hours=24))
    start_time = timezone.now() - window_delta
    
    # Parse frequency to get SQL date format
    freq_format_mapping = {
        '1m': "strftime('%%Y-%%m-%%d %%H:%%M:00', timestamp)",
        '5m': "strftime('%%Y-%%m-%%d %%H:', timestamp) || (CAST(strftime('%%M', timestamp) AS INTEGER) / 5) * 5 || ':00'",
        '15m': "strftime('%%Y-%%m-%%d %%H:', timestamp) || (CAST(strftime('%%M', timestamp) AS INTEGER) / 15) * 15 || ':00'",
        '1h': "strftime('%%Y-%%m-%%d %%H:00:00', timestamp)",
        '1d': "date(timestamp)"
    }
    
    freq_format = freq_format_mapping.get(freq, freq_format_mapping['5m'])
    
    # Aggregate events by time bucket and event name
    daily_stats = queryset.filter(
        timestamp__gte=start_time
    ).extra(
        select={'time_bucket': freq_format}
    ).values('time_bucket', 'event_name').annotate(
        count=Count('id')
    ).order_by('time_bucket', 'event_name')
    
    # Get total event counts by event name
    event_counts = queryset.values('event_name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get event counts by source
    source_counts = queryset.values('source').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get recent events for live feed
    recent_events = queryset.order_by('-timestamp')[:20]
    recent_events_data = EventSerializer(recent_events, many=True).data
    
    return Response({
        'daily_stats': list(daily_stats),
        'event_counts': list(event_counts),
        'source_counts': list(source_counts),
        'recent_events': recent_events_data,
        'total_events': queryset.count(),
        'time_window': time_window,
        'freq': freq
    })

@api_view(['GET'])
def get_events(request):
    # Optional project filtering via API key
    api_key = request.GET.get('api_key')
    queryset = Event.objects.all()
    
    if api_key:
        try:
            project = Project.objects.get(api_key=api_key, is_active=True)
            queryset = queryset.filter(project=project)
        except Project.DoesNotExist:
            return Response({'error': 'Invalid API key'}, status=status.HTTP_401_UNAUTHORIZED)
    
    events = queryset.order_by('-timestamp')[:50]  # Last 50 events
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT'])
def project_settings(request):
    """Get or update project settings for the authenticated project"""
    # Get API key from appropriate location based on request method
    if request.method == 'GET':
        api_key = request.GET.get('api_key')
    else:  # PUT
        api_key = request.data.get('api_key')
    
    if not api_key:
        return Response({'error': 'API key is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        project = Project.objects.get(api_key=api_key, is_active=True)
    except Project.DoesNotExist:
        return Response({'error': 'Invalid API key'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Create a copy of request data without the api_key for serializer
        data = request.data.copy()
        data.pop('api_key', None)
        
        serializer = ProjectSerializer(project, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_projects(request):
    """Get all available projects for project selector"""
    projects = Project.objects.filter(is_active=True).order_by('name')
    projects_data = []
    
    for project in projects:
        projects_data.append({
            'id': project.id,
            'name': project.name,
            'slug': project.slug,
            'api_key': project.api_key,
            'is_default': project.is_default,
        })
    
    return Response(projects_data)