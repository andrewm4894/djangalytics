from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from .models import Event
from .serializers import EventCreateSerializer, EventSerializer

@api_view(['POST'])
def capture_event(request):
    serializer = EventCreateSerializer(data=request.data)
    if serializer.is_valid():
        event = serializer.save()
        return Response({
            'id': event.id,
            'event_name': event.event_name,
            'timestamp': event.timestamp,
            'message': 'Event captured successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_stats(request):
    # Get events from the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    # Aggregate events by date and event name
    daily_stats = Event.objects.filter(
        timestamp__gte=seven_days_ago
    ).extra(
        select={'date': "date(timestamp)"}
    ).values('date', 'event_name', 'source').annotate(
        count=Count('id')
    ).order_by('date', 'event_name')
    
    # Get total event counts by event name
    event_counts = Event.objects.values('event_name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get event counts by source
    source_counts = Event.objects.values('source').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get recent events for live feed
    recent_events = Event.objects.all()[:20]
    recent_events_data = EventSerializer(recent_events, many=True).data
    
    return Response({
        'daily_stats': list(daily_stats),
        'event_counts': list(event_counts),
        'source_counts': list(source_counts),
        'recent_events': recent_events_data,
        'total_events': Event.objects.count()
    })

@api_view(['GET'])
def get_events(request):
    events = Event.objects.all()[:50]  # Last 50 events
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)