########################
# metering/admin.py
########################

from django.contrib import admin

from metering.models import (
    Meter,
    BalanceSlot,
    IntervalReading,
)


@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    # ✅ NUR sichere Felder verwenden
    list_display = (
        "id",
        "owner_user",  # ✅ neu
        "meter_type",  # ✅ neu
    )

    # ✅ WICHTIG: FK korrekt durchsuchen
    search_fields = (
        "id",
        "owner_user__email",
        "owner_user__username",
    )

    list_filter = (
        "owner_user",
        "meter_type",
    )


@admin.register(IntervalReading)
class IntervalReadingAdmin(admin.ModelAdmin):
    list_display = ("meter_id", "ts_start", "value")
    ordering = ("-ts_start",)


@admin.register(BalanceSlot)
class BalanceSlotAdmin(admin.ModelAdmin):
    list_display = (
        "meter_id",
        "period_start",
        "consumption_kwh",
    )
    ordering = ("-period_start",)
