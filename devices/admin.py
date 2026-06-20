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
        "safe_floor",
        "role",
        "configured",
        "last_seen",
    )

    list_filter = ("configured", "role", "home")
    search_fields = ("identifier", "name", "room__name")
    ordering = ("-created_at",)

    # ----------------------------
    # SAFE FIELDS (no 500 errors)
    # ----------------------------

    def safe_name(self, obj):
        return obj.name or "-"
    safe_name.short_description = "Name"

    def safe_room(self, obj):
        return obj.room.name if obj.room else "-"
    safe_room.short_description = "Room"

    def safe_floor(self, obj):
        return obj.floor.name if obj.floor else "-"
    safe_floor.short_description = "Floor"


# =============================
# DEVICE METRIC
# =============================

@admin.register(DeviceMetric)
class DeviceMetricAdmin(admin.ModelAdmin):
    list_display = (
        "safe_device",
        "metric",
        "value",
        "unit",
        "timestamp",
    )

    list_filter = ("metric",)
    search_fields = ("metric",)

    ordering = ("-timestamp",)

    def safe_device(self, obj):
        return obj.device.identifier if obj.device else "-"
    safe_device.short_description = "Device"

    def get_queryset(self, request):
        # ✅ verhindert FK / join Probleme + schneller
        return super().get_queryset(request).select_related("device")


# =============================
# SUPPORT MODELS
# =============================

@admin.register(DeviceRole)
class DeviceRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "label")
    search_fields = ("key", "label")



@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "floor")
