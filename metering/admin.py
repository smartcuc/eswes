########################
# metering/admin.py
########################


from django.contrib import admin
from .models import (
    Tenant,
    Member,
    MemberEnergyProfile,
    Meter,
    MeterRegister,
    IntervalReading,
    AggregatedReading,
)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "user", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "tenant")
    search_fields = ("user__email", "tenant__name")
    raw_id_fields = ("user", "tenant")


@admin.register(MemberEnergyProfile)
class MemberEnergyProfileAdmin(admin.ModelAdmin):
    list_display = ("member", "energy_role", "grid_connection_id", "created_at")
    list_filter = ("energy_role",)
    raw_id_fields = ("member",)


@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "serial_number",
        "tenant",
        "owner_user",
        "owner_member",
        "meter_type",
    )
    list_filter = ("meter_type", "tenant")
    search_fields = ("serial_number",)
    raw_id_fields = ("tenant", "owner_user", "owner_member")


@admin.register(MeterRegister)
class MeterRegisterAdmin(admin.ModelAdmin):
    list_display = ("id", "meter", "obis_code", "description")
    search_fields = ("meter__serial_number", "obis_code")
    raw_id_fields = ("meter",)


@admin.register(IntervalReading)
class IntervalReadingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "meter",
        "ts_start",
        "obis_code",
        "value",
        "unit",
        "source",
    )
    list_filter = ("tenant", "obis_code", "unit", "source")
    search_fields = ("meter__serial_number", "obis_code")
    raw_id_fields = ("tenant", "meter")


@admin.register(AggregatedReading)
class AggregatedReadingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "meter",
        "period_start",
        "period_type",
        "obis_code",
        "value",
    )
    list_filter = ("tenant", "period_type", "obis_code")
    search_fields = ("meter__serial_number", "obis_code")
    raw_id_fields = ("tenant", "meter", "member")
