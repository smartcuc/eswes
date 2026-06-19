##################
# devices/admin.py
##################

from django.contrib import admin
from .models import Device, DeviceMetric, Home


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
        "created_at",
    )
    list_filter = ("configured", "role", "home")
    search_fields = ("identifier", "name", "room")
    ordering = ("-created_at",)


@admin.register(DeviceMetric)
class DeviceMetricAdmin(admin.ModelAdmin):
    list_display = ("device", "created_at")
    search_fields = ("device__identifier",)
    ordering = ("-created_at",)


