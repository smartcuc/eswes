################################################
# accounts/management/commands/cleanup_tokens.py
################################################

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from accounts.models import MagicLoginToken

class Command(BaseCommand):
    help = "Delete old magic login tokens"

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(days=2)

        qs = MagicLoginToken.objects.filter(created_at__lt=cutoff)

        count = qs.count()
        qs.delete()

        self.stdout.write(f"Deleted {count} old tokens")
