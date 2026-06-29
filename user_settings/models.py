#########################
# user_settings/models.py
# #######################

from django.conf import settings
from django.db import models


class UserPreference(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferences",
    )

    key = models.CharField(max_length=100)

    value = models.JSONField(default=dict)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "key"],
                name="unique_user_preference",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.key}"


