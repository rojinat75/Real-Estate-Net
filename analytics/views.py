from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.sessions.models import Session
from django.contrib.auth.models import AnonymousUser

from .models import PageView, SocialShare, SocialShareAnalytics
from properties.models import Property
from blog.models import BlogPost
import json
from django.utils import timezone

def track_event(request, pk):
    property = Property.objects.get(pk=pk)
    user = request.user if request.user.is_authenticated else None
    PageView.objects.create(property=property, user=user)
    # This view doesn't render a template, it just records the event.
    # You might return an HttpResponse or redirect to the property detail page.
    return render(request, 'analytics/track_event.html') # Placeholder for now

@method_decorator(csrf_exempt, name='dispatch')
class TrackSocialShare(View):
    """
    API endpoint to track social sharing events
    """
    def post(self, request):
        try:
            data = json.loads(request.body)

            # Extract required fields
            platform = data.get('platform')
            content_type = data.get('content_type', 'other')
            page_title = data.get('page_title', '')
            url_shared = data.get('url', '')

            # Optional fields
            content_id = data.get('content_id')
            metadata = data.get('metadata', {})

            # Get user and session info
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Determine content type and get the object
            property_obj = None
            blog_post_obj = None

            if content_type == 'property' and content_id:
                try:
                    property_obj = Property.objects.get(pk=content_id)
                except Property.DoesNotExist:
                    pass

            elif content_type == 'blog_post' and content_id:
                try:
                    blog_post_obj = BlogPost.objects.get(pk=content_id)
                except BlogPost.DoesNotExist:
                    pass

            # Create the SocialShare record
            social_share = SocialShare.objects.create(
                user=user,
                property=property_obj,
                blog_post=blog_post_obj,
                platform=platform,
                content_type=content_type,
                url_shared=url_shared,
                page_title=page_title,
                ip_address=ip_address,
                user_agent=user_agent,
                session_key=session_key,
                referrer=request.META.get('HTTP_REFERER', ''),
                metadata=metadata
            )

            # Update daily analytics
            self.update_daily_analytics(social_share)

            return JsonResponse({
                'success': True,
                'message': f'Share to {platform} recorded successfully',
                'share_id': social_share.id
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    def get_client_ip(self, request):
        """Get client IP address, handling proxy headers"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def update_daily_analytics(self, social_share):
        """Update the daily social share analytics"""
        today = timezone.now().date()

        # Get or create analytics record
        analytics, created = SocialShareAnalytics.objects.get_or_create(
            date=today,
            platform=social_share.platform,
            defaults={
                'total_shares': 0,
                'unique_users': 0,
                'property_shares': 0,
                'blog_shares': 0,
                'other_shares': 0
            }
        )

        # Update counters
        analytics.total_shares += 1

        # Track unique users (we'll use IP + user as unique identifier)
        user_identifier = social_share.user.id if social_share.user else social_share.ip_address
        # For simplicity, we'll just increment unique_users for now
        # In a production system, you'd track unique users per day
        analytics.unique_users += 1

        # Update content type counters
        if social_share.content_type == 'property':
            analytics.property_shares += 1
        elif social_share.content_type == 'blog_post':
            analytics.blog_shares += 1
        else:
            analytics.other_shares += 1

        analytics.save()

def get_social_share_stats(request):
    """Get social sharing statistics for dashboard"""
    from django.db.models import Count, Sum
    from django.db.models.functions import TruncDate

    # Get last 30 days of data
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=30)

    # Aggregate share data by platform
    platform_stats = SocialShare.objects.filter(
        timestamp__date__range=[start_date, end_date]
    ).values('platform').annotate(
        total_shares=Count('id'),
        unique_users=Count('ip_address', distinct=True) if hasattr(SocialShare.objects, 'distinct') else Count('id')
    ).order_by('-total_shares')

    # Daily breakdown for charts
    daily_stats = SocialShare.objects.filter(
        timestamp__date__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(
        total_shares=Count('id')
    ).order_by('date')

    return JsonResponse({
        'platform_stats': list(platform_stats),
        'daily_stats': list(daily_stats),
        'total_shares': SocialShare.objects.filter(
            timestamp__date__range=[start_date, end_date]
        ).count(),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    })
