######################
# operations/models.py
######################

from django.db import models


class HealthState(models.Model):

    key = models.CharField(
        max_length=100,
        unique=True,
    )

    status = models.CharField(
        max_length=20,
    )

    value = models.TextField(
        blank=True,
        default="",
    )

    details = models.JSONField(
        default=dict,
        blank=True,
    )

    checked_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return f"{self.key}: {self.status}"
