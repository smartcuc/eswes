#
# core/management/commands/seed_base.py
#

from django.core.management.base import BaseCommandfrom django.core.management.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Seed base system users (admin + test user)"


    def handle(self, *args, **options):

        with transaction.atomic():

            # ✅ Admin User
            admin, created = User.objects.get_or_create(
                username="admin",
                defaults={
                    "email": "admin@sharegy.de",
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                },
            )

            if created:
                admin.set_password("admin123")
                admin.save()

            # ✅ Test User
            user, created = User.objects.get_or_create(
                username="testuser",
                defaults={
                    "email": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "is_active": True,
                },
            )

            if created:
                user.set_password("testpass123")
                user.save()

        self.stdout.write(
            self.style.SUCCESS("✅ Base users created (admin + testuser)")
        )

