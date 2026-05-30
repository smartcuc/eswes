################################################
# energy/management/commands/publish_commands.py
################################################


from django.core.management.base import BaseCommand
from energy.tasks import publish_pending_device_commands


class Command(BaseCommand):
    help = "Publish queued DeviceCommands via MQTT."

    def add_arguments(self, parser):
        parser.add_argument("--batch", type=int, default=25)

    def handle(self, *args, **opts):
        res = publish_pending_device_commands.apply(
            args=(), kwargs={"batch_size": opts["batch"]}
        ).get()
        self.stdout.write(self.style.SUCCESS(f"Published: {res}"))
