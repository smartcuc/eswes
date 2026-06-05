########################
# metering/admin.py
########################

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.db.models import (
    OuterRef,
    Subquery,
    DateTimeField,
    ExpressionWrapper,
    DurationField,
)
from django.db.models.functions import Now

from metering.models import IntervalReading

from .models import (
    Tenant,
    Member,
    MemberEnergyProfile,
    Meter,
    MeterRegister,
    IntervalReading,
    AggregatedReading,
)

# ✅ --------------------------------
# Tenant / Member (unverändert)
# ✅ --------------------------------


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


# ✅ --------------------------------
# 🔥 METER ADMIN (MIT DEBUG + OPTIMIZED)
# ✅ --------------------------------


@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):

    fields = (
        "serial_number",
        "tenant",
        "owner_user",
        "owner_member",
        "meter_type",
        "integration_type",
        "tibber_home_id",
        "last_tibber_sync",
    )

    readonly_fields = ("last_tibber_sync",)

    list_display = (
        "id",
        "serial_number",
        "tenant",
        "owner_user",
        "owner_member",
        "meter_type",
        # ✅ Debug
        "integration_type",
        "last_reading",
        "delay_minutes",
        "status_colored",
    )

    list_filter = (
        "meter_type",
        "tenant",
        "integration_type",
    )

    search_fields = ("serial_number", "tibber_home_id")

    raw_id_fields = ("tenant", "owner_user", "owner_member")

    ordering = ("serial_number",)

    # ✅ ---------------------------
    # 🔥 Mini-Optimierung (Subquery)
    # ✅ ---------------------------

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        latest_reading = (
            IntervalReading.objects.filter(meter=OuterRef("pk"))
            .order_by("-ts_start")
            .values("ts_start")[:1]
        )

        qs = qs.annotate(
            last_reading_ts=Subquery(
                latest_reading,
                output_field=DateTimeField(),
            )
        )

        return qs

    # ✅ ---------------------------
    # 📊 Debug Fields
    # ✅ ---------------------------

    def last_reading(self, obj):
        return obj.last_reading_ts

    last_reading.short_description = "Last Reading"

    def delay_minutes(self, obj):
        if not obj.last_reading_ts:
            return None

        delta = timezone.now() - obj.last_reading_ts
        return int(delta.total_seconds() / 60)

    delay_minutes.short_description = "Delay (min)"

    # ✅ ---------------------------
    # 🎨 Schöner Status (colored)
    # ✅ ---------------------------

    def status_colored(self, obj):
        if not obj.last_reading_ts:
            return format_html("<span style='color:{};'>{}</span>", "gray", "no_data")

        delay = self.delay_minutes(obj)

        if delay < 60:
            return format_html("<b style='color:{};'>{}</b>", "green", "ok")
        elif delay < 180:
            return format_html("<b style='color:{};'>{}</b>", "orange", "delayed")
        else:
            return format_html("<b style='color:{};'>{}</b>", "red", "stale")

    status_colored.allow_tags = True


# ✅ --------------------------------
# Rest (unverändert)
# ✅ --------------------------------


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
