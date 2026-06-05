###########################
# market/models_analysis.py
###########################

import uuid
from django.db import models


class SpotPriceDaySummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    date = models.DateField(unique=True)

    cheapest_hour = models.DateTimeField()
    cheapest_hour_price = models.DecimalField(max_digits=10, decimal_places=6)

    best_2h_start = models.DateTimeField()
    best_2h_price = models.DecimalField(max_digits=10, decimal_places=6)

    best_3h_start = models.DateTimeField()
    best_3h_price = models.DecimalField(max_digits=10, decimal_places=6)

    best_5h_start = models.DateTimeField()
    best_5h_price = models.DecimalField(max_digits=10, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} summary"
