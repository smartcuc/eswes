##################################
# energy/ems/models_signal_type.py
##################################

from django.db import models


class EMSSignalType(models.Model):

    key = models.CharField(
        max_length=50,
        unique=True,
    )

    label = models.CharField(
        max_length=100,
    )

    active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.label
