################
# demo/models.py
################

from django.db import models

from devices.models import Device


class DemoDeviceMap(models.Model):

    source_device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="demo_sources",
    )

    demo_device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="demo_targets",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = (
            "source_device",
            "demo_device",
        )

    def __str__(self):
        return (
            f"{self.source_device_id}"
            f" -> "
            f"{self.demo_device_id}"
        )

