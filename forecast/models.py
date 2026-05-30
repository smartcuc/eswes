####################
# forecast/models.py
####################


import uuid
from django.db import models


class SolarForecast(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey("metering.Tenant", on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    forecast_kwh = models.DecimalField(max_digits=12, decimal_places=3)

    source = models.CharField(max_length=50, default="forecast")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "timestamp")
        indexes = [models.Index(fields=["tenant", "timestamp"])]

    def __str__(self):
        return f"{self.tenant} {self.timestamp} → {self.forecast_kwh} kWh"
