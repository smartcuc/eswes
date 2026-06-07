###################
# billing/models.py
###################

import uuid
from django.db import models
from core.ownership import owner_xor_constraints


class BankAccount(models.Model):
    """
    Bankdaten: Standalone oder Tenant-Kontext.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    iban = models.CharField(max_length=34)
    bic = models.CharField(max_length=20, blank=True)
    account_holder = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["tenant", "is_active"])]
        constraints = owner_xor_constraints("bankaccount")

    def __str__(self):
        return f"{self.account_holder} ({'tenant' if self.owner_member_id else 'standalone'})"


class Contract(models.Model):
    """
    Minimaler Vertrag (später erweiterbar).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    CONTRACT_TYPE = [
        ("supply", "Supply"),
        ("sharing", "Sharing"),
        ("dynamic", "Dynamic pricing supply"),
    ]
    contract_type = models.CharField(
        max_length=20, choices=CONTRACT_TYPE, default="supply"
    )

    supplier_name = models.CharField(max_length=255, blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = owner_xor_constraints("contract")

    def __str__(self):
        return f"{self.contract_type} ({self.supplier_name})"


class UserMeterAssignment(models.Model):
    """
    Genau ein aktiver Billing-User pro Meter.
    Ein User kann mehrere Meter haben.
    Ein Meter gehört nicht mehreren Billing-Usern gleichzeitig.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="meter_assignments",
    )
    meter = models.ForeignKey(
        "metering.Meter",
        on_delete=models.CASCADE,
        related_name="billing_assignments",
    )

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["meter", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["meter"],
                condition=models.Q(is_active=True),
                name="uniq_active_assignment_per_meter",
            )
        ]

    def __str__(self):
        return f"{self.user} ← {self.meter}"


class UserBalanceSlot(models.Model):
    """
    Billing-/Abrechnungs-Sicht pro User und Meter und Slot.
    Grundlage: BalanceSlot (pro Meter).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="balance_slots",
    )
    meter = models.ForeignKey(
        "metering.Meter",
        on_delete=models.CASCADE,
        related_name="user_balance_slots",
    )

    period_start = models.DateTimeField()

    consumption_kwh = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    generation_kwh = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    self_consumption_kwh = models.DecimalField(
        max_digits=12, decimal_places=6, default=0
    )
    grid_import_kwh = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    grid_export_kwh = models.DecimalField(max_digits=12, decimal_places=6, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "period_start"]),
            models.Index(fields=["meter", "period_start"]),
            models.Index(fields=["tenant", "period_start"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "meter", "period_start"],
                name="uniq_user_meter_period",
            )
        ]

    def __str__(self):
        return f"{self.user} / {self.meter} @ {self.period_start}"
