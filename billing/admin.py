##################
# billing/admin.py
##################

from django.contrib import admin
from .models import BankAccount, Contract


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "account_holder",
        "iban",
        "tenant",
        "owner_user",
        "owner_membership",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "tenant")
    search_fields = ("account_holder", "iban", "bic")
    raw_id_fields = ("tenant", "owner_user", "owner_membership")


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "contract_type",
        "supplier_name",
        "start_date",
        "end_date",
        "tenant",
        "owner_user",
        "owner_membership",
    )
    list_filter = ("contract_type", "tenant")
    search_fields = ("supplier_name",)
    raw_id_fields = ("tenant", "owner_user", "owner_membership")
