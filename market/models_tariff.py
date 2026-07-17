#########################
# market/models_tariff.py
#########################

import uuid

from django.db import models
from devices.models import Home

class HomeTariff(models.Model):

    TARIFF_DYNAMIC = "dynamic"
    TARIFF_STATIC = "static"

    TARIFF_CHOICES = [
        (TARIFF_DYNAMIC, "Dynamic"),
        (TARIFF_STATIC, "Static"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="tariffs",
    )

    valid_from = models.DateField()

    tariff_type = models.CharField(
        max_length=20,
        choices=TARIFF_CHOICES,
        default=TARIFF_DYNAMIC,
    )

    static_price_eur_per_kwh = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = ["-valid_from"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "home",
                    "valid_from",
                ],
                name="unique_home_tariff_date",
            ),
        ]

    def __str__(self):

        return f"{self.home.name} | " f"{self.tariff_type} | " f"{self.valid_from}"
