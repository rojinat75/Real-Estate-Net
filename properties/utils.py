"""
Image validation and fake detection utilities for property images
"""
import os
import hashlib
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Image


def calculate_image_hash(image_file):
    """Calculate hash of image file for duplicate detection"""
    hash_md5 = hashlib.md5()
    for chunk in image_file.chunks():
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


def detect_duplicate_images():
    """Find and mark duplicate images based on file hash"""
    from django.db.models import Count

    # Group images by hash and find duplicates
    duplicates = Image.objects.values('image').annotate(
        count=Count('id')
    ).filter(count__gt=1)

    marked_count = 0
    for duplicate in duplicates:
        # Get all images with the same hash
        duplicate_images = Image.objects.filter(image=duplicate['image'])

        # Mark all but the first as duplicates
        master_image = duplicate_images.first()
        for img in duplicate_images[1:]:
            img.is_duplicate = True
            img.duplicate_of = master_image
            img.save()
            marked_count += 1

    return marked_count


def validate_image_file(image):
    """Validate uploaded image file"""
    errors = []

    # Check file size (max 10MB)
    if image.size > 10 * 1024 * 1024:
        errors.append("File size too large. Maximum 10MB allowed.")

    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_extension = os.path.splitext(image.name)[1].lower()

    if file_extension not in allowed_extensions:
        errors.append(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")

    return errors


def detect_fake_images():
    """Detect and flag suspicious images for admin review"""
    flagged_count = 0

    # Get all images that haven't been processed yet
    images_to_check = Image.objects.filter(
        status__in=['pending', 'approved']
    ).select_related('property')

    for image in images_to_check:
        suspicious_reasons = []

        # Check file size (too small might be fake)
        if image.file_size and image.file_size < 10240:  # Less than 10KB
            suspicious_reasons.append("File size too small")

        # Check dimensions (too small might be fake)
        if image.width and image.height:
            if image.width < 300 or image.height < 300:
                suspicious_reasons.append("Image dimensions too small")

        # Check if it's a duplicate
        if image.is_duplicate:
            suspicious_reasons.append("Marked as duplicate")

        # Check for common fake image patterns
        if image.caption and len(image.caption) < 5:
            suspicious_reasons.append("Caption too short")

        # Flag if suspicious
        if suspicious_reasons:
            image.flag_for_review(
                None,  # No specific admin user for automated detection
                f"Automated detection: {', '.join(suspicious_reasons)}"
            )
            flagged_count += 1

    return flagged_count


def get_image_statistics():
    """Get statistics about property images"""
    from django.db.models import Count, Avg, Sum, Q

    stats = Image.objects.aggregate(
        total_images=Count('id'),
        approved_images=Count('id', filter=Q(status='approved')),
        rejected_images=Count('id', filter=Q(status='rejected')),
        flagged_images=Count('id', filter=Q(status='flagged')),
        deleted_images=Count('id', filter=Q(status='deleted')),
        avg_file_size=Avg('file_size'),
        total_file_size=Sum('file_size'),
        duplicate_images=Count('id', filter=Q(is_duplicate=True)),
    )

    # Add percentage calculations
    if stats['total_images'] > 0:
        stats['approved_percentage'] = (stats['approved_images'] / stats['total_images']) * 100
        stats['rejected_percentage'] = (stats['rejected_images'] / stats['total_images']) * 100
        stats['flagged_percentage'] = (stats['flagged_images'] / stats['total_images']) * 100
        stats['deleted_percentage'] = (stats['deleted_images'] / stats['total_images']) * 100
        stats['duplicate_percentage'] = (stats['duplicate_images'] / stats['total_images']) * 100
    else:
        stats.update({
            'approved_percentage': 0,
            'rejected_percentage': 0,
            'flagged_percentage': 0,
            'deleted_percentage': 0,
            'duplicate_percentage': 0,
        })

    return stats


def cleanup_orphaned_files():
    """Clean up image files that are no longer referenced in database"""
    from django.conf import settings
    import os

    media_root = settings.MEDIA_ROOT
    property_images_path = os.path.join(media_root, 'property_images')

    if not os.path.exists(property_images_path):
        return 0

    # Get all image files in the directory
    image_files = set()
    for root, dirs, files in os.walk(property_images_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                image_files.add(os.path.join(root, file))

    # Get all image paths from database
    db_image_paths = set()
    for image in Image.objects.all():
        if image.image:
            db_image_paths.add(image.image.path)

    # Find orphaned files
    orphaned_files = image_files - db_image_paths
    deleted_count = 0

    for file_path in orphaned_files:
        try:
            os.remove(file_path)
            deleted_count += 1
        except OSError:
            pass  # File might be already deleted or inaccessible

    return deleted_count


def send_image_moderation_notification(image, action, admin_user=None):
    """Send notification to property owner about image moderation"""
    from django.core.mail import send_mail
    from django.conf import settings

    if not hasattr(settings, 'DEFAULT_FROM_EMAIL'):
        return  # Email not configured

    try:
        subject = f"Property Image {action.title()} - {image.property.title}"
        message = f"""
Dear {image.property.user.get_full_name() or image.property.user.username},

Your property image for "{image.property.title}" has been {action}.

Action: {action.title()}
Property: {image.property.title}
Image Caption: {image.caption or 'No caption'}

"""

        if action == 'deleted' and image.deletion_reason:
            message += f"Reason: {image.deletion_reason}\n\n"

        message += """
If you believe this action was taken in error, please contact our support team.

Best regards,
Real Estate Net Team
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[image.property.user.email],
            fail_silently=True,
        )
    except Exception:
        pass  # Email sending failed, but don't break the moderation process
