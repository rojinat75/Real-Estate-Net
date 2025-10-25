from django.core.management.base import BaseCommand
from django.utils import timezone
from properties.models import Image
from properties.utils import detect_fake_images, get_image_statistics


class Command(BaseCommand):
    help = 'Detect and flag fake property images for admin review'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be flagged without actually flagging',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limit number of images to process (0 = all)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']

        self.stdout.write(
            self.style.SUCCESS('🔍 Starting fake image detection...')
        )

        # Get images to process
        images_to_check = Image.objects.filter(
            status__in=['pending', 'approved']
        ).select_related('property')

        if limit > 0:
            images_to_check = images_to_check[:limit]

        total_images = images_to_check.count()
        self.stdout.write(f'📊 Processing {total_images} images...')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN MODE - No changes will be made')
            )

        flagged_count = 0
        suspicious_images = []

        for i, image in enumerate(images_to_check, 1):
            if i % 100 == 0:
                self.stdout.write(f'  Progress: {i}/{total_images} images processed...')

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

            # Check if already flagged
            if image.status == 'flagged':
                suspicious_reasons.append("Already flagged")

            # Flag if suspicious
            if suspicious_reasons:
                suspicious_images.append({
                    'image': image,
                    'reasons': suspicious_reasons
                })

                if not dry_run:
                    image.flag_for_review(
                        None,  # No specific admin user for automated detection
                        f"Automated detection: {', '.join(suspicious_reasons)}"
                    )
                    flagged_count += 1

        # Show results
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Detection complete!')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'📋 Would flag {len(suspicious_images)} images:')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'🚩 Flagged {flagged_count} images for review:')
            )

        for item in suspicious_images[:10]:  # Show first 10
            image = item['image']
            reasons = ', '.join(item['reasons'])
            self.stdout.write(
                f'  • {image.property.title} - {reasons}'
            )

        if len(suspicious_images) > 10:
            self.stdout.write(
                f'  ... and {len(suspicious_images) - 10} more images'
            )

        # Show statistics
        stats = get_image_statistics()
        self.stdout.write(f'\n📊 Image Statistics:')
        self.stdout.write(f'  • Total images: {stats["total_images"]}')
        self.stdout.write(f'  • Approved: {stats["approved_images"]} ({stats["approved_percentage"]:.1f}%)')
        self.stdout.write(f'  • Flagged: {stats["flagged_images"]} ({stats["flagged_percentage"]:.1f}%)')
        self.stdout.write(f'  • Rejected: {stats["rejected_images"]} ({stats["rejected_percentage"]:.1f}%)')
        self.stdout.write(f'  • Deleted: {stats["deleted_images"]} ({stats["deleted_percentage"]:.1f}%)')
        self.stdout.write(f'  • Duplicates: {stats["duplicate_images"]} ({stats["duplicate_percentage"]:.1f}%)')

        if not dry_run and flagged_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎯 Next steps:')
            )
            self.stdout.write(f'  • Review flagged images at: /real-admin/properties/image/review-queue/')
            self.stdout.write(f'  • Use bulk actions to approve or reject images')
            self.stdout.write(f'  • Check image details for more information')
