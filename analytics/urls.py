from django.urls import path
from . import views

urlpatterns = [
    path('capture_event/', views.capture_event, name='capture_event'),
    path('stats/', views.get_stats, name='get_stats'),
    path('events/', views.get_events, name='get_events'),
]