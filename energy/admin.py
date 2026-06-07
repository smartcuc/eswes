#################
# energy/admin.py
#################


from django.contrib import admin
from .models import (
    Location,
    EnergyAsset,
    EnergyAssetPV,
    EnergyAssetBattery,
    EnergyAssetEV,
    AssetMeter,
    Device,
    SmartEnergySettings,
)

from energy.models import DeviceCommand


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "tenant",
        "owner_user",
        "owner_membership",
        "city",
        "postal_code",
    )
    list_filter = ("tenant", "city", "country")
    search_fields = ("name", "street", "city", "postal_code")
    raw_id_fields = ("tenant", "owner_user", "owner_membership")


@admin.register(EnergyAsset)
class EnergyAssetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "asset_type",
        "tenant",
        "owner_user",
        "owner_membership",
        "installed_power_kw",
        "installed_at",
    )
    list_filter = ("asset_type", "tenant")
    search_fields = ("name",)
    raw_id_fields = ("tenant", "owner_user", "owner_membership", "location")


@admin.register(EnergyAssetPV)
class EnergyAssetPVAdmin(admin.ModelAdmin):
    list_display = (
        "asset",
        "module_manufacturer",
        "inverter_manufacturer",
        "tilt_angle",
        "azimuth",
    )
    search_fields = ("module_manufacturer", "inverter_manufacturer")
    raw_id_fields = ("asset",)


@admin.register(EnergyAssetBattery)
class EnergyAssetBatteryAdmin(admin.ModelAdmin):
    list_display = (
        "asset",
        "capacity_kwh",
        "usable_capacity_kwh",
        "max_charge_kw",
        "max_discharge_kw",
        "efficiency",
    )
    search_fields = ("manufacturer", "model")
    raw_id_fields = ("asset",)


@admin.register(EnergyAssetEV)
class EnergyAssetEVAdmin(admin.ModelAdmin):
    list_display = ("asset", "battery_capacity_kwh", "max_charging_power_kw")
    raw_id_fields = ("asset",)


@admin.register(AssetMeter)
class AssetMeterAdmin(admin.ModelAdmin):
    list_display = ("id", "asset", "meter", "relation_type", "created_at")
    list_filter = ("relation_type",)
    search_fields = ("asset__name", "meter__serial_number")
    raw_id_fields = ("asset", "meter")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "device_type",
        "controllable",
        "tenant",
        "owner_user",
        "owner_membership",
        "created_at",
    )
    list_filter = ("device_type", "controllable", "tenant")
    search_fields = ("name",)
    raw_id_fields = ("tenant", "owner_user", "owner_membership", "location", "asset")


@admin.register(SmartEnergySettings)
class SmartEnergySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "owner_user",
        "owner_membership",
        "optimization_mode",
        "allow_direct_control",
        "optimize_ev",
        "optimize_battery",
    )
    list_filter = ("optimization_mode", "allow_direct_control")
    raw_id_fields = ("tenant", "owner_user", "owner_membership")


@admin.register(DeviceCommand)
class DeviceCommandAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "device",
        "command",
        "status",
        #       "attempts",
        "ts_created",
        "ts_sent",
        "ts_ack",
    )
    list_filter = ("status", "command")
    search_fields = ("device__name", "command", "dedup_key")
