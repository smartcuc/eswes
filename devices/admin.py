##################
# devices/admin.py
##################

from django.contrib import admin
from .models import Home, Device, DeviceMetric, DeviceRole, Floor, Room


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "mqtt_token", "created_at")
    search_fields = ("name", "user__email")
    ordering = ("-created_at",)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "identifier",
        "name",
        "configured",
        "role",
        "home",
        "floor",
        "room",
        "last_seen",
        "created_at",
    )
    list_filter = ("configured", "role", "home", "floor")
    search_fields = ("identifier", "name", "room__name")
    ordering = ("-created_at",)


@admin.register(DeviceMetric)
class DeviceMetricAdmin(admin.ModelAdmin):
    list_display = ("device", "metric", "value", "unit", "timestamp")
    search_fields = ("device__identifier", "metric")
    ordering = ("-timestamp",)


admin.site.register(DeviceRole)
admin.site.register(Floor)
admin.site.register(Room)
