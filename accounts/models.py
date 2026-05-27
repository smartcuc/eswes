#####################
# accounts/models.py
#####################

from django.contrib.auth.models import AbstractUser
from django.db import models
from metering.models import Tenant


class User(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("member", "Member"),
        ("viewer", "Viewer"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
