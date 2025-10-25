from django.urls import path
from . import views

app_name = 'analytics'
urlpatterns = [
    # Existing views
    path('track/<int:pk>/', views.track_event, name='track_event'),

    # Social sharing tracking
    path('track-share/', views.TrackSocialShare.as_view(), name='track_social_share'),
    path('share-stats/', views.get_social_share_stats, name='social_share_stats'),
]
