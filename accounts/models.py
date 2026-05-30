####################
# accounts/models.py
####################


import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Identity Layer (global).
    Keine Tenant-Abhängigkeiten hier!
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Person-/Kundendaten (tenant-unabhängig).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Adresse
    street = models.CharField(max_length=255, blank=True)
    house_number = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, default="DE")

    # Kontakt
    phone = models.CharField(max_length=30, blank=True)

    # Typ
    customer_type = models.CharField(
        max_length=20,
        choices=[("private", "Private"), ("business", "Business")],
        default="private",
    )

    # Business optional
    company_name = models.CharField(max_length=255, blank=True)
    vat_id = models.CharField(max_length=50, blank=True)

    # DSGVO / Consent
    consent_given = models.BooleanField(default=False)
    consent_timestamp = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class UserSettings(models.Model):
    """
    Standalone Dashboard / Präferenzen (tenant-unabhängig).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")

    DASHBOARD_MODE = [("simple", "Simple"), ("advanced", "Advanced")]
    dashboard_mode = models.CharField(
        max_length=20, choices=DASHBOARD_MODE, default="simple"
    )

    # UX-Hinweis: nicht als Berechtigung verwenden
    USAGE_MODE = [
        ("standalone", "Standalone"),
        ("tenant", "Tenant"),
        ("hybrid", "Hybrid"),
    ]
    usage_mode = models.CharField(
        max_length=20, choices=USAGE_MODE, default="standalone"
    )

    created_at = models.DateTimeField(auto_now_add=True)


class UserSettings(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)

    usage_mode = models.CharField(
        max_length=20,
        choices=[
            ("standalone", "Standalone"),
            ("tenant", "Tenant"),
            ("hybrid", "Hybrid"),
        ],
        default="standalone",
    )

    dashboard_mode = models.CharField(
        max_length=20,
        choices=[
            ("simple", "Simple"),
            ("advanced", "Advanced"),
        ],
        default="simple",
    )

    created_at = models.DateTimeField(auto_now_add=True)
