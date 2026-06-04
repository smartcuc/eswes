##################
# billing/admin.py
##################

from django.contrib import admin
from .models import (
    BankAccount,
    Contract,
    DirtySlot,
    UserBalanceSlot,
)


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant_id", "iban", "name")


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant_id", "user_id")


@admin.register(DirtySlot)
class DirtySlotAdmin(admin.ModelAdmin):
    list_display = ("meter_id", "period_start", "created_at")
    ordering = ("-period_start",)


@admin.register(UserBalanceSlot)
class UserBalanceSlotAdmin(admin.ModelAdmin):
    list_display = ("user_id", "meter_id", "period_start", "consumption_kwh")
    ordering = ("-period_start",)
