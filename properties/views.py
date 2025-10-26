from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Property, SavedSearch
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import PropertySearchForm, PropertyForm
from django.contrib import messages
from django.shortcuts import redirect
import random


def broker_required(view_func):
    """
    Decorator to check if user is a broker
    """
    def check_user(user):
        return user.is_authenticated and user.user_type == 'broker'
    return user_passes_test(check_user, login_url='accounts:login', redirect_field_name='next')(view_func)


def home(request):
    if request.user.is_authenticated:
        # Get featured/premium properties (limit to 6)
        featured_properties = Property.objects.filter(is_premium=True)[:6]

        # Get latest properties (limit to 8)
        latest_properties = Property.objects.all().order_by('-created_at')[:8]

        context = {
            'featured_properties': featured_properties,
            'latest_properties': latest_properties,
            'show_properties': True,  # Flag to show property sections
        }
    else:
        context = {
            'show_properties': False,  # Flag to hide property sections
        }
    return render(request, 'home.html', context)

@login_required(login_url='/accounts/login/')
def property_list(request):
    properties = Property.objects.all()

    # Get filter parameters
    property_type_filter = request.GET.get('property_type')
    listing_type_filter = request.GET.get('listing_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    city_filter = request.GET.get('city')
    view_mode = request.GET.get('view', 'grid')  # Default to grid view

    # Apply filters
    if property_type_filter:
        # For now, we'll filter by property type name (this should be improved with proper property type filtering)
        properties = properties.filter(property_type__name__icontains=property_type_filter)

    if listing_type_filter:
        if listing_type_filter == 'sale':
            properties = properties.filter(status='for_sale')
        elif listing_type_filter == 'lease':
            properties = properties.filter(status='for_lease')

    if min_price:
        try:
            properties = properties.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            properties = properties.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if city_filter:
        properties = properties.filter(city__icontains=city_filter)

    # Add related images to properties for template use
    properties = properties.prefetch_related('images')

    # Prepare data for map markers using actual property coordinates
    properties_data = []
    for prop in properties:
        # Use property's location coordinates if available, otherwise fallback to Kathmandu
        lat = getattr(prop.location, 'latitude', None) or 27.7172
        lng = getattr(prop.location, 'longitude', None) or 85.3240

        # Add slight randomization if multiple properties have same coordinates
        same_coords = [p for p in properties_data if p['lat'] == lat and p['lng'] == lng]
        if same_coords:
            lat += random.uniform(-0.01, 0.01)
            lng += random.uniform(-0.01, 0.01)

        properties_data.append({
            'title': prop.title,
            'lat': lat,
            'lng': lng,
            'url': f'/properties/{prop.pk}/',
            'is_premium': prop.is_premium
        })

    context = {
        'properties': properties,
        'view_mode': view_mode,
        'properties_data': properties_data,
    }
    return render(request, 'properties/property_list.html', context)

@login_required(login_url='/accounts/login/')
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    context = {
        'property': property
    }
    return render(request, 'properties/property_detail.html', context)

@login_required(login_url='/accounts/login/')
def search_results(request):
    form = PropertySearchForm(request.GET)
    properties = Property.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        property_type = form.cleaned_data.get('property_type')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        min_sq_ft = form.cleaned_data.get('min_sq_ft')
        max_sq_ft = form.cleaned_data.get('max_sq_ft')
        amenities = form.cleaned_data.get('amenities')
        city = form.cleaned_data.get('city')
        state = form.cleaned_data.get('state')
        zip_code = form.cleaned_data.get('zip_code')
        lease_or_buy = form.cleaned_data.get('lease_or_buy')
        cap_rate = form.cleaned_data.get('cap_rate')
        year_built = form.cleaned_data.get('year_built')
        zoning = form.cleaned_data.get('zoning')

        if query:
            properties = properties.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(state__icontains=query) |
                Q(zip_code__icontains=query)
            )
        if property_type:
            properties = properties.filter(property_type=property_type)
        if min_price:
            properties = properties.filter(price__gte=min_price)
        if max_price:
            properties = properties.filter(price__lte=max_price)
        if min_sq_ft:
            properties = properties.filter(square_footage__gte=min_sq_ft)
        if max_sq_ft:
            properties = properties.filter(square_footage__lte=max_sq_ft)
        if amenities:
            for amenity in amenities:
                properties = properties.filter(amenities=amenity)
        if city:
            properties = properties.filter(city__icontains=city)
        if state:
            properties = properties.filter(state__icontains=state)
        if zip_code:
            properties = properties.filter(zip_code__icontains=zip_code)
        if lease_or_buy:
            properties = properties.filter(status=lease_or_buy)
        if cap_rate:
            properties = properties.filter(cap_rate__gte=cap_rate)
        if year_built:
            properties = properties.filter(year_built=year_built)
        if zoning:
            properties = properties.filter(zoning__icontains=zoning)

    context = {
        'form': form,
        'properties': properties
    }
    return render(request, 'properties/search_results.html', context)

@broker_required
def property_create(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.user = request.user
            property_obj.save()
            form.save_m2m() # Save ManyToMany relations
            messages.success(request, "Property created successfully.")
            return redirect('properties:property_detail', pk=property_obj.pk)
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PropertyForm()
    return render(request, 'properties/property_form.html', {'form': form, 'action': 'Create'})

@login_required
def property_update(request, pk):
    property = get_object_or_404(Property, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, "Property updated successfully.")
            return redirect('properties:property_detail', pk=property.pk)
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PropertyForm(instance=property)

    return render(request, 'properties/property_form.html', {'form': form, 'action': 'Update'})

@login_required
def property_delete(request, pk):
    property = get_object_or_404(Property, pk=pk, user=request.user)
    if request.method == 'POST':
        property.delete()
        messages.success(request, "Property deleted successfully.")
        return redirect('properties:property_list')
    return render(request, 'properties/property_confirm_delete.html', {'property': property})

@login_required
def save_search(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        filters = request.POST.get('filters')
        if name:
            SavedSearch.objects.create(
                user=request.user,
                name=name,
                filters=filters or '',
                alert_enabled=request.POST.get('alert_enabled') == 'on'
            )
            messages.success(request, "Search saved successfully.")
        else:
            messages.error(request, "Please provide a name for the search.")
    return redirect('properties:search_results')
