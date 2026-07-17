#################################
# market/models_price_config.py
#################################

import uuid

from django.db import models


class ElectricityPriceConfig(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    valid_from = models.DateField(
        unique=True,
    )

    grid_fee_ct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=0,
    )

    electricity_tax_ct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=0,
    )

    concession_fee_ct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=0,
    )

    kwk_levy_ct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=0,
    )

    special_grid_levy_ct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=0,
    )

    offshore_levy_ct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=0,
    )

    vat_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=19.00,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-valid_from"]

    def additional_costs_ct(self):

        return (
            self.grid_fee_ct
            + self.electricity_tax_ct
            + self.concession_fee_ct
            + self.kwk_levy_ct
            + self.special_grid_levy_ct
            + self.offshore_levy_ct
        )

    def __str__(self):

        return f"Electricity Config " f"({self.valid_from})"
