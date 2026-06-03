###################
# billing/models.py
###################

import uuid
from django.db import models


class DirtySlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    meter_id = models.UUIDField()
    period_start = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "billing_dirtyslot"
        indexes = [
            models.Index(fields=["meter_id", "period_start"]),
        ]


class UserBalanceSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.UUIDField()
    meter_id = models.UUIDField()
    tenant_id = models.UUIDField(null=True, blank=True)

    period_start = models.DateTimeField()

    consumption_kwh = models.FloatField(default=0)
    generation_kwh = models.FloatField(default=0)
    self_consumption_kwh = models.FloatField(default=0)
    grid_import_kwh = models.FloatField(default=0)
    grid_export_kwh = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "billing_userbalanceslot"
        managed = False  # ✅ wichtig wegen Timescale
