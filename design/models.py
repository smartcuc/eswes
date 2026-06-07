##################
# design/models.py
##################

from django.db import models


class TenantTheme(models.Model):
    tenant = models.OneToOneField(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="theme",
    )

    primary = models.CharField(max_length=20)
    secondary = models.CharField(max_length=20)
    button = models.CharField(max_length=20)

    def __str__(self):
        return f"Theme for {self.tenant.name}"
