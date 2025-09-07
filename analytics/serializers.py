from rest_framework import serializers
from .models import Event, Project
from .utils import generate_anonymous_user_id, generate_session_id, get_client_ip, parse_user_agent

class EventSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'event_name', 'source', 'timestamp', 'properties', 'project_name', 'user_id', 'session_id', 'user_agent', 'ip_address']
        
class EventCreateSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True, help_text='Project API key for authentication')
    
    class Meta:
        model = Event
        fields = ['event_name', 'source', 'timestamp', 'properties', 'api_key', 'user_id', 'session_id', 'user_agent', 'ip_address']
        extra_kwargs = {
            'timestamp': {'required': False},
            'source': {'required': False, 'default': 'web'},
            'user_id': {'required': False},
            'session_id': {'required': False},
            'user_agent': {'required': False},
            'ip_address': {'required': False}
        }
    
    def validate_api_key(self, value):
        try:
            project = Project.objects.get(api_key=value, is_active=True)
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError('Invalid or inactive API key')
    
    def validate(self, attrs):
        api_key = attrs.pop('api_key')
        project = Project.objects.get(api_key=api_key, is_active=True)
        
        # Check if source is allowed
        source = attrs.get('source', 'web')
        if not project.is_source_allowed(source):
            raise serializers.ValidationError({
                'source': f'Source "{source}" is not allowed for this project'
            })
        
        # Generate user_id if not provided
        user_id = attrs.get('user_id')
        if not user_id:
            # Try to get from request context
            request = self.context.get('request')
            if request:
                user_id = generate_anonymous_user_id(request)
            else:
                # Fallback for non-request contexts (like tests)
                user_id = generate_anonymous_user_id()
            attrs['user_id'] = user_id
        
        # Generate session_id if not provided
        session_id = attrs.get('session_id')
        if not session_id:
            session_id = generate_session_id(user_id)
            attrs['session_id'] = session_id
        
        # Store project for use in create method
        attrs['project'] = project
        return attrs
    
    def create(self, validated_data):
        project = validated_data.pop('project')
        
        # Always extract request metadata for analytics (override client-provided values for security)
        request = self.context.get('request')
        if request:
            # Always use server-side extracted values for security
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            validated_data['ip_address'] = get_client_ip(request)
        
        event = Event.objects.create(project=project, **validated_data)
        return event

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'slug', 'api_key', 'allowed_sources', 'rate_limit_per_minute', 'is_active', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'api_key', 'created_at', 'updated_at']