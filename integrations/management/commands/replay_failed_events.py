##########################################################
# integrations/management/commands/replay_failed_events.py
##########################################################

from django.core.management.base import BaseCommand
from integrations.models import InboundWebhookEvent
from integrations.tasks import process_inbound_webhook_event


class Command(BaseCommand):
    help = "Replays failed webhook events"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        limit = options["limit"]

        events = InboundWebhookEvent.objects.filter(
            status=InboundWebhookEvent.Status.ERROR
        ).order_by("received_at")[:limit]

        count = 0
        for evt in events:
            process_inbound_webhook_event.delay(str(evt.id))
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Replayed {count} events"))
