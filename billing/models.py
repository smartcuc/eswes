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
        "metering.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_member = models.ForeignKey(
        "metering.Member", on_delete=models.CASCADE, null=True, blank=True
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
    Minimaler Vertrag (später erweitern: Tarif, Laufzeit, Lieferant etc.).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "metering.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_member = models.ForeignKey(
        "metering.Member", on_delete=models.CASCADE, null=True, blank=True
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
