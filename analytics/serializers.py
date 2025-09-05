from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'event_name', 'source', 'timestamp', 'properties']
        
class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['event_name', 'source', 'timestamp', 'properties']
        extra_kwargs = {
            'timestamp': {'required': False},
            'source': {'required': False}
        }