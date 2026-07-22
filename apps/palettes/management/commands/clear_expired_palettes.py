from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.palettes.models import Palette

class Command(BaseCommand):
    help = "Permanently deletes palettes in the recycle bin for more than 30 days."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=30)
        expired_palettes = Palette.objects.filter(is_active=False, deleted_at__lt=cutoff)
        count = expired_palettes.count()
        
        # Deleting the palettes triggers deletion of related palette colors cascade
        expired_palettes.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully purged {count} expired palettes from the recycle bin."
            )
        )
