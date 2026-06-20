##################
# devices/admin.py
##################

from django.contrib import admin
from .models import Home, Device, DeviceMetric, DeviceRole, Floor, Room


# =============================
# HOME
# =============================

@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "mqtt_token", "created_at")
    search_fields = ("name", "user__email")
    ordering = ("-created_at",)


# =============================
# DEVICE
# =============================

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "identifier",
        "safe_name",
        "home",
        "safe_room",
        "role",
        "configured",
        "last_seen",
    )

    list_filter = ("configured", "role", "home")
    search_fields = ("identifier", "name", "room__name")
    ordering = ("-created_at",)

    def safe_name(self, obj):
        return obj.name or "-"
    safe_name.short_description = "Name"

    def safe_room(self, obj):
        return obj.room.name if obj.room else "-"
    safe_room.short_description = "Room"


# =============================
# DEVICE METRIC
# =============================

@admin.register(DeviceMetric)
class DeviceMetricAdmin(admin.ModelAdmin):
    list_display = ("safe_device", "metric", "value", "unit", "timestamp")

    list_filter = ("metric", "device__home")
    search_fields = ("device__identifier", "metric")

    ordering = ("-timestamp",)

    def safe_device(self, obj):
        return obj.device.identifier if obj.device else "-"
    safe_device.short_description = "Device"

    def get_queryset(self, request):
        # ✅ Performance + verhindert select errors
        return super().get_queryset(request).select_related("device")


# =============================
# SIMPLE MODELS
# =============================

admin.site.register(DeviceRole)
admin.site.register(Floor)
admin.site.register(Room)
