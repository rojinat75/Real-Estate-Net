from django.shortcuts import render
from .models import PageView
from properties.models import Property

def track_event(request, pk):
    property = Property.objects.get(pk=pk)
    user = request.user if request.user.is_authenticated else None
    PageView.objects.create(property=property, user=user)
    # This view doesn't render a template, it just records the event.
    # You might return an HttpResponse or redirect to the property detail page.
    return render(request, 'analytics/track_event.html') # Placeholder for now
