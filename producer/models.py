#####################
# producer/models.py
#####################

import uuid

from django.db import models

from devices.models import Home, Device


class GeneratorType(models.Model):

    key = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=100,
    )

    active = models.BooleanField(
        default=True,
    )

    sort_order = models.IntegerField(
        default=0,
    )

    class Meta:

        ordering = [
            "sort_order",
            "name",
        ]

        verbose_name = "Generator Typ"
        verbose_name_plural = "Generator Typen"

        def __str__(self):
            return self.name


class Orientation(models.Model):

    key = models.CharField(
        max_length=10,
        unique=True,
    )

    name = models.CharField(
        max_length=50,
    )

    azimuth_deg = models.IntegerField()

    sort_order = models.IntegerField(
        default=0,
    )

    active = models.BooleanField(
        default=True,
    )

    class Meta:

        ordering = [
                "sort_order",
            ]

        verbose_name = "Ausrichtung"
        verbose_name_plural = "Ausrichtungen"

    def __str__(self):
        return self.name


class GeneratorSystem(models.Model):

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

    device = models.OneToOneField(
        Device,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generator_system",
    )

    name = models.CharField(
        max_length=100,
    )

    generator_type = models.ForeignKey(
        GeneratorType,
        on_delete=models.PROTECT,
        related_name="generator_systems",
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

    orientation = models.ForeignKey(
        Orientation,
        on_delete=models.PROTECT,
        related_name="strings",
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

    def __str__(self):

        return f"{self.generator.name} | " f"{self.name}"

    @property
    def azimuth_deg(self):

        return self.orientation.azimuth_deg
