####################
# forecast/models.py
####################

import uuid
from django.db import models
from tenants.models import Tenant


class SolarForecast(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    forecast_kwh = models.DecimalField(max_digits=12, decimal_places=3)

    source = models.CharField(max_length=50, default="forecast")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_forecast_per_source",
                fields=["tenant", "timestamp", "source"],
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "timestamp"], name="forecast_tenant_ts_idx"),
            models.Index(
                fields=["tenant", "source", "timestamp"],
                name="forecast_tenant_source_ts_idx",
            ),
        ]

    def __str__(self):
        return f"{self.tenant} {self.timestamp} → {self.forecast_kwh} kWh"


class TenantWeatherSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="weather_snapshots",
    )

    ts = models.DateTimeField()

    temperature_c = models.FloatField(null=True, blank=True)
    cloud_cover_pct = models.FloatField(null=True, blank=True)
    shortwave_radiation_wm2 = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "ts"],
                name="unique_weather_snapshot_per_tenant_ts",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "ts"], name="weather_tenant_ts_idx"),
        ]

    def __str__(self):
        return f"{self.tenant} @ {self.ts}"
