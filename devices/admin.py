##################
# devices/admin.py
##################

from django.contrib import admin
from .models import *


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "identifier", "home")


@admin.register(DeviceConfig)
class DeviceConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "device",
        "name",
        "role",
        "energy_source",
        "energy_group",
    )

    list_filter = (
        "role",
        "energy_source",
        "energy_group",
        "home",
    )


@admin.register(DeviceMetric)
class DeviceMetricAdmin(admin.ModelAdmin):
    list_display = ("id", "device", "metric_key", "value", "timestamp")


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user")


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(DeviceRole)
class DeviceRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "label")


@admin.register(MetricDefinition)
class MetricDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "name", "unit")


@admin.register(EnergySource)
class EnergySourceAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "label")
    search_fields = ("key", "label")


@admin.register(EnergyGroup)
class EnergyGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "label")
    search_fields = ("key", "label")
    