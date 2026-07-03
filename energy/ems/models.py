#########################
# energy/ems/models.py
#########################

from django.db import models


class EMSSignalSource(models.Model):

    SIGNAL_TYPES = [
        ("pv", "PV"),
        ("grid", "Netz"),
    ]

    home = models.ForeignKey(
        "devices.Home",
        on_delete=models.CASCADE,
        related_name="ems_signal_sources",
    )

    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="ems_signal_sources",
    )

    signal_type = models.CharField(
        max_length=20,
        choices=SIGNAL_TYPES,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        indexes = [
            models.Index(
                fields=[
                    "home",
                    "signal_type",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.home} | "
            f"{self.signal_type} | "
            f"{self.device}"
        )
    