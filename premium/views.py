from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta
from properties.models import Property
from accounts.models import User
from .models import PremiumListing, PromoCode
from .forms import PremiumListingForm
from . import utils
import uuid

def premium_form(request):
    """General premium upgrade form - allows users to choose which property to upgrade"""
    if request.user.is_authenticated:
        # Get plan from URL parameter
        selected_plan = request.GET.get('plan', '')

        # Get user's properties that aren't already premium
        available_properties = Property.objects.filter(
            user=request.user
        ).exclude(
            premium_listing__isnull=False
        )

        if request.method == 'POST':
            property_id = request.POST.get('property_id')
            plan_type = request.POST.get('plan_type', selected_plan)

            if property_id and plan_type:
                # Redirect to QR payment page
                return redirect('premium:qr_payment', plan_type=plan_type, property_pk=property_id)

        context = {
            'available_properties': available_properties,
            'selected_plan': selected_plan,
        }
        return render(request, 'premium/premium_form.html', context)
    else:
        # Redirect to login if not authenticated
        return redirect('accounts:login')

@login_required
def premium_create(request, property_pk):
    property = get_object_or_404(Property, pk=property_pk, user=request.user)
    if hasattr(property, 'premium_listing'):
        messages.warning(request, "This property already has a premium listing.")
        return redirect('property_detail', pk=property.pk)

    if request.method == 'POST':
        form = PremiumListingForm(request.POST)
        if form.is_valid():
            premium_listing = form.save(commit=False)
            premium_listing.property = property
            premium_listing.save()
            messages.success(request, "Premium listing created successfully.")
            return redirect('property_detail', pk=property.pk)
    else:
        form = PremiumListingForm(initial={'property': property})
    return render(request, 'premium/premium_form.html', {'form': form, 'property': property, 'action': 'Create'})

@login_required
def premium_update(request, pk):
    premium_listing = get_object_or_404(PremiumListing, pk=pk, property__user=request.user)
    if request.method == 'POST':
        form = PremiumListingForm(request.POST, instance=premium_listing)
        if form.is_valid():
            form.save()
            messages.success(request, "Premium listing updated successfully.")
            return redirect('property_detail', pk=premium_listing.property.pk)
    else:
        form = PremiumListingForm(instance=premium_listing)
    return render(request, 'premium/premium_form.html', {'form': form, 'premium_listing': premium_listing, 'action': 'Update'})

@login_required
def premium_delete(request, pk):
    premium_listing = get_object_or_404(PremiumListing, pk=pk, property__user=request.user)
    if request.method == 'POST':
        premium_listing.delete()
        messages.success(request, "Premium listing deleted successfully.")
        return redirect('property_detail', pk=premium_listing.property.pk)
    return render(request, 'premium/premium_confirm_delete.html', {'premium_listing': premium_listing})

def premium_badge(request):
    return render(request, 'premium/premium_badge.html')

@login_required
def premium_dashboard(request):
    """Premium user dashboard showing all their premium listings and analytics"""
    user_premium_listings = PremiumListing.objects.filter(
        property__user=request.user,
        is_active=True
    )

    # Get analytics for user's premium properties
    premium_properties = Property.objects.filter(
        user=request.user,
        is_premium=True
    )

    context = {
        'premium_listings': user_premium_listings,
        'premium_properties': premium_properties,
        'total_premium': user_premium_listings.count(),
        'active_listings': user_premium_listings.filter(is_active=True).count(),
        'expiring_soon': user_premium_listings.filter(
            end_date__lte=timezone.now() + timedelta(days=7)
        ).count(),
    }
    return render(request, 'premium/premium_dashboard.html', context)

def premium_plans(request):
    """Display available premium plans and pricing"""
    plans = [
        {
            'name': 'Basic Premium',
            'duration': '1 Week',
            'price': 500,  # NPR
            'features': [
                'Featured in search results',
                'Priority placement',
                'Basic analytics',
                'Email support'
            ]
        },
        {
            'name': 'Featured Listing',
            'duration': '1 Month',
            'price': 2000,  # NPR
            'features': [
                'All Basic features',
                'Top placement in search',
                'Detailed analytics',
                'Social media promotion',
                'Priority support'
            ]
        },
        {
            'name': 'Premium Plus',
            'duration': '3 Months',
            'price': 5000,  # NPR
            'features': [
                'All Featured features',
                'Homepage spotlight',
                'Advanced analytics',
                'Virtual tour hosting',
                'Dedicated support'
            ]
        }
    ]

    context = {
        'plans': plans,
    }
    return render(request, 'premium/premium_plans.html', context)

def payment_methods(request):
    """Display available payment methods"""
    return render(request, 'premium/payment_methods.html')

@login_required
def qr_payment(request, plan_type, property_pk):
    """Generate QR code payment for premium upgrade"""
    property = get_object_or_404(Property, pk=property_pk, user=request.user)

    # Plan pricing
    plan_prices = {
        'basic': 500,      # 1 week
        'featured': 2000,  # 1 month
        'premium': 5000,   # 3 months
    }

    plan_durations = {
        'basic': 7,        # days
        'featured': 30,    # days
        'premium': 90,     # days
    }

    price = plan_prices.get(plan_type, 500)
    duration_days = plan_durations.get(plan_type, 7)
    payment_id = f"QR_{uuid.uuid4().hex[:8].upper()}"

    context = {
        'property': property,
        'plan_type': plan_type,
        'price': price,
        'duration_days': duration_days,
        'payment_id': payment_id,
        'user': request.user,
        'payment_date': timezone.now(),
    }
    return render(request, 'premium/qr_payment.html', context)

@login_required
def payment_processing(request, plan_type, property_pk, payment_method):
    """Show payment processing simulation"""
    property = get_object_or_404(Property, pk=property_pk, user=request.user)

    # Plan pricing
    plan_prices = {
        'basic': 500,      # 1 week
        'featured': 2000,  # 1 month
        'premium': 5000,   # 3 months
    }

    plan_durations = {
        'basic': 7,        # days
        'featured': 30,    # days
        'premium': 90,     # days
    }

    price = plan_prices.get(plan_type, 500)
    duration_days = plan_durations.get(plan_type, 7)

    # Calculate subscription dates
    start_date = timezone.now()
    end_date = start_date + timedelta(days=duration_days)

    # Simulate payment processing result
    # In real app, this would be webhook/callback result
    payment_success = process_payment_simulation(payment_method, price, request.user)

    if payment_success['success']:
        # Create premium listing
        premium_listing = PremiumListing.objects.create(
            property=property,
            user=request.user,
            plan_type=plan_type,
            amount_paid=price,
            payment_method=payment_method,
            payment_status='completed',
            payment_reference=payment_success.get('reference', ''),
            payment_details=payment_success,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        # Update property premium status
        property.is_premium = True
        property.save()

        # Send success email
        utils.send_premium_activated_email(request.user, property, premium_listing)

        messages.success(request, f"Premium listing activated successfully! Your property '{property.title}' is now premium.")

    else:
        # Log failed payment attempt
        utils.send_payment_failed_email(request.user, property, plan_type, price,
                                      payment_success.get('payment_id', 'N/A'))
        messages.error(request, "Payment failed. Please try again or contact support.")

    context = {
        'property': property,
        'plan_type': plan_type,
        'payment_method': payment_method,
        'price': price,
        'duration_days': duration_days,
        'start_date': start_date,
        'end_date': end_date,
        'payment_date': start_date,
        'payment_success': payment_success['success'],
        'payment_details': payment_success,
    }
    return render(request, 'premium/payment_processing.html', context)

@login_required
def premium_checkout(request, plan_type, property_pk):
    """Payment checkout simulation for premium upgrade"""
    property = get_object_or_404(Property, pk=property_pk, user=request.user)

    # Plan pricing
    plan_prices = {
        'basic': 500,      # 1 week
        'featured': 2000,  # 1 month
        'premium': 5000,   # 3 months
    }

    plan_durations = {
        'basic': 7,        # days
        'featured': 30,    # days
        'premium': 90,     # days
    }

    original_price = plan_prices.get(plan_type, 500)
    duration_days = plan_durations.get(plan_type, 7)
    discount_amount = 0
    discounted_price = original_price
    promo_code_obj = None

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        promo_code = request.POST.get('promo_code', '').strip().upper()

        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect('premium:premium_checkout', plan_type=plan_type, property_pk=property_pk)

        # Validate promo code if provided
        if promo_code:
            try:
                promo_obj = PromoCode.objects.get(code=promo_code, is_active=True)
                if promo_obj.is_valid():
                    discount_amount = promo_obj.apply_discount(original_price)
                    discounted_price = promo_obj.apply_discount(original_price)
                    if promo_obj.use_code():
                        messages.success(request, f"Promo code applied! You saved NPR {discount_amount:.2f}")
                        promo_code_obj = promo_obj
                    else:
                        messages.error(request, "Sorry, this promo code has reached its usage limit.")
                        return redirect('premium:premium_checkout', plan_type=plan_type, property_pk=property_pk)
                else:
                    messages.error(request, "Invalid or expired promo code.")
                    return redirect('premium:premium_checkout', plan_type=plan_type, property_pk=property_pk)
            except PromoCode.DoesNotExist:
                messages.error(request, "Promo code not found.")
                return redirect('premium:premium_checkout', plan_type=plan_type, property_pk=property_pk)

        # Store promo code info in session for payment processing
        request.session['promo_code'] = promo_code_obj.code if promo_code_obj else None
        request.session['discount_amount'] = discount_amount
        request.session['final_price'] = discounted_price

        # Redirect to payment processing page
        return redirect('premium:payment_processing', plan_type=plan_type, property_pk=property_pk, payment_method=payment_method)

    # Handle GET request - check for existing promo code application
    applied_promo = request.GET.get('promo', '').strip().upper()
    applied_discount = 0
    applied_price = original_price

    if applied_promo:
        try:
            promo_obj = PromoCode.objects.get(code=applied_promo, is_active=True)
            if promo_obj.is_valid():
                applied_discount = promo_obj.apply_discount(original_price)
                applied_price = promo_obj.apply_discount(original_price)
                promo_code_obj = promo_obj
                messages.success(request, f"Promo code applied! Save NPR {applied_discount:.2f}")
            else:
                messages.error(request, "Invalid or expired promo code.")
        except PromoCode.DoesNotExist:
            messages.error(request, "Promo code not found.")

    context = {
        'property': property,
        'plan_type': plan_type,
        'original_price': original_price,
        'price': applied_price,
        'discounted_price': applied_price,
        'discount_amount': applied_discount,
        'duration_days': duration_days,
        'promo_code': promo_code_obj,
    }
    return render(request, 'premium/premium_checkout.html', context)

def process_payment_simulation(payment_method, amount, user):
    """Simulate payment processing for different methods"""
    import time
    from random import choice

    # Simulate processing time
    time.sleep(1)

    payment_id = f"PAY_{uuid.uuid4().hex[:8].upper()}"

    # Simulate different success rates based on payment method
    success_rates = {
        'esewa': 0.95,
        'khalti': 0.93,
        'credit_card': 0.90,
        'bank_transfer': 0.85,
        'mobile_banking': 0.88,
        'cash': 1.0,  # Always successful for cash
    }

    success_rate = success_rates.get(payment_method, 0.80)

    # Simulate random success/failure
    if choice([True, False]) or success_rate >= 0.9:  # Higher success rate for demo
        return {
            'success': True,
            'payment_id': payment_id,
            'reference': f"REF_{uuid.uuid4().hex[:6].upper()}",
            'details': {
                'method': payment_method,
                'amount': amount,
                'currency': 'NPR',
                'processed_at': timezone.now().isoformat(),
                'status': 'completed'
            }
        }
    else:
        return {
            'success': False,
            'payment_id': payment_id,
            'error': f"{payment_method.upper()} payment failed. Please try again or use a different payment method."
        }

@login_required
def premium_analytics(request):
    """Detailed analytics for premium users"""
    user_properties = Property.objects.filter(user=request.user, is_premium=True)

    # Get analytics data
    total_views = 0
    total_inquiries = 0
    property_analytics = []

    for prop in user_properties:
        views = prop.page_views.count()
        inquiries = prop.contactinquiry_set.count()
        total_views += views
        total_inquiries += inquiries

        property_analytics.append({
            'property': prop,
            'views': views,
            'inquiries': inquiries,
            'conversion_rate': (inquiries / views * 100) if views > 0 else 0
        })

    context = {
        'total_views': total_views,
        'total_inquiries': total_inquiries,
        'property_analytics': property_analytics,
        'avg_conversion_rate': (total_inquiries / total_views * 100) if total_views > 0 else 0,
    }
    return render(request, 'premium/premium_analytics.html', context)

def admin_create_premium(request):
    """Admin view to manually create premium listings for users"""
    from django.contrib.admin.views.decorators import staff_member_required

    @staff_member_required
    def admin_premium_create(request):
        if request.method == 'POST':
            property_id = request.POST.get('property_id')
            user_id = request.POST.get('user_id')
            plan_type = request.POST.get('plan_type', 'basic')
            amount_paid = request.POST.get('amount_paid', 0)
            duration_days = request.POST.get('duration_days', 30)

            try:
                property = Property.objects.get(id=property_id)
                user = User.objects.get(id=user_id)

                # Calculate end date
                end_date = timezone.now() + timedelta(days=int(duration_days))

                # Create premium listing
                premium_listing = PremiumListing.objects.create(
                    property=property,
                    user=user,
                    plan_type=plan_type,
                    amount_paid=amount_paid,
                    payment_id=f"ADMIN_{uuid.uuid4().hex[:8].upper()}",
                    end_date=end_date,
                    is_active=True
                )

                # Update property premium status
                property.is_premium = True
                property.save()

                messages.success(
                    request,
                    f"Premium listing created for {user.username}'s property '{property.title}'"
                )
                return redirect('admin:premium_premiumlisting_changelist')

            except (Property.DoesNotExist, User.DoesNotExist) as e:
                messages.error(request, f"Error: {str(e)}")

        # Get all properties and users for selection
        properties = Property.objects.all().order_by('-created_at')[:50]
        users = User.objects.filter(user_type='broker').order_by('username')

        context = {
            'properties': properties,
            'users': users,
            'plan_types': PremiumListing.PLAN_CHOICES,
        }
        return render(request, 'admin/premium_create.html', context)

    return admin_premium_create(request)
