#####################
# producer/models.py
#####################

import uuid

from django.db import models

from devices.models import Home


class GeneratorSystem(models.Model):

    TYPE_PV = "pv"
    TYPE_FUEL_CELL = "fuel_cell"
    TYPE_DIESEL = "diesel"
    TYPE_CHP = "chp"
    TYPE_WIND = "wind"

    SYSTEM_TYPES = [
        (TYPE_PV, "Photovoltaik"),
        (TYPE_FUEL_CELL, "Brennstoffzelle"),
        (TYPE_DIESEL, "Dieselgenerator"),
        (TYPE_CHP, "Blockheizkraftwerk"),
        (TYPE_WIND, "Windenergie"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="generator_systems",
    )

    name = models.CharField(
        max_length=100,
    )

    system_type = models.CharField(
        max_length=20,
        choices=SYSTEM_TYPES,
    )

    peak_power_kw = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Gesamtleistung des Systems in kW/kWp",
    )

    inverter_power_kw = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Wechselrichterleistung",
    )

    battery_capacity_kwh = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Speicherkapazität",
    )

    active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "name",
        ]

    def __str__(self):

        return f"{self.home.name} | " f"{self.name}"
