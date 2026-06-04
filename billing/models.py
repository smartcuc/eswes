###################
# billing/models.py
###################

import uuid
from django.db import models

# =========================================================
# ✅ DOMAIN MODELS (für Admin / Business Logik)
# =========================================================


class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    tenant_id = models.UUIDField(null=True, blank=True)
    iban = models.CharField(max_length=64, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "billing_bankaccount"
        managed = False


class Contract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    tenant_id = models.UUIDField(null=True, blank=True)
    user_id = models.UUIDField(null=True, blank=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "billing_contract"
        managed = False


# =========================================================
# ✅ DIRTY PIPELINE (aktiv genutzt)
# =========================================================


class DirtySlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    meter_id = models.UUIDField()
    period_start = models.DateTimeField()

    created_at = models.DateTimeField()

    class Meta:
        db_table = "billing_dirtyslot"


# =========================================================
# ✅ USER BALANCE (SQL gesteuert)
# =========================================================


class UserBalanceSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user_id = models.UUIDField()
    meter_id = models.UUIDField()
    tenant_id = models.UUIDField(null=True)

    period_start = models.DateTimeField()

    consumption_kwh = models.FloatField()
    generation_kwh = models.FloatField()

    self_consumption_kwh = models.FloatField()
    grid_import_kwh = models.FloatField()
    grid_export_kwh = models.FloatField()

    created_at = models.DateTimeField()

    class Meta:
        db_table = "billing_userbalanceslot"
        managed = False
