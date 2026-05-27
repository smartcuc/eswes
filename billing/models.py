###################
# billing/models.py
###################


from django.db import models
from metering.models import Tenant  # ✅ DAS fehlt!


class Tariff(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    price_per_kwh = models.DecimalField(max_digits=6, decimal_places=3)
    valid_from = models.DateTimeField()


class Invoice(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    total_kwh = models.DecimalField(max_digits=12, decimal_places=3)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)


class SpotPrice(models.Model):
    timestamp = models.DateTimeField(unique=True)
    price_eur_per_kwh = models.DecimalField(max_digits=10, decimal_places=5)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} → {self.price_eur_per_kwh} €/kWh"
