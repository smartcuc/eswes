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

    @property
    def string_count(self):

        return self.strings.count()

    @property
    def total_string_power_kwp(self):

        return sum(float(s.peak_power_kwp) for s in self.strings.all())
    

    def __str__(self):

        return f"{self.home.name} | " f"{self.name}"


class GeneratorString(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    generator = models.ForeignKey(
        GeneratorSystem,
        on_delete=models.CASCADE,
        related_name="strings",
    )

    name = models.CharField(
        max_length=100,
    )

    module_count = models.PositiveIntegerField(
        default=0,
    )

    peak_power_kwp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    ORIENTATION_N = "N"
    ORIENTATION_NE = "NE"
    ORIENTATION_E = "E"
    ORIENTATION_SE = "SE"
    ORIENTATION_S = "S"
    ORIENTATION_SW = "SW"
    ORIENTATION_W = "W"
    ORIENTATION_NW = "NW"

    ORIENTATION_CHOICES = [
        (ORIENTATION_N, "Nord"),
        (ORIENTATION_NE, "Nordost"),
        (ORIENTATION_E, "Ost"),
        (ORIENTATION_SE, "Südost"),
        (ORIENTATION_S, "Süd"),
        (ORIENTATION_SW, "Südwest"),
        (ORIENTATION_W, "West"),
        (ORIENTATION_NW, "Nordwest"),
    ]

    orientation = models.CharField(
        max_length=2,
        choices=ORIENTATION_CHOICES,
        default=ORIENTATION_S,
    )
    tilt_deg = models.IntegerField(
        default=35,
        help_text="Dachneigung",
    )

    shading_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "name",
        ]

    @property
    def azimuth_deg(self):

        mapping = {
            "N": 0,
            "NE": 45,
            "E": 90,
            "SE": 135,
            "S": 180,
            "SW": 225,
            "W": 270,
            "NW": 315,
        }

        return mapping[self.orientation]

    def __str__(self):

        return f"{self.generator.name} | " f"{self.name}"
