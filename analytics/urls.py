from django.urls import path
from . import views

app_name = 'analytics'
urlpatterns = [
    path('track/<int:pk>/', views.track_event, name='track_event'),
]
