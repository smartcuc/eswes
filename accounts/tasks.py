###################
# accounts/tasks.py
###################


from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from accounts.models import MagicLoginToken


@shared_task
def cleanup_tokens():
    cutoff = timezone.now() - timedelta(days=2)
    qs = MagicLoginToken.objects.filter(created_at__lt=cutoff)

    count = qs.count()
    qs.delete()

    return f"Deleted {count} tokens"
