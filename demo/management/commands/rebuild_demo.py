##########################################
# demo/management/commands/rebuild_demo.py
##########################################

from django.core.management.base import BaseCommand

from demo.services.rebuild_demo import (
    rebuild_demo_environment,
)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        result = rebuild_demo_environment()

        self.stdout.write(self.style.SUCCESS(str(result)))
