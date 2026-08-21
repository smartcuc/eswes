##################
# devices/admin.py
##################

from django.contrib import admin
from .models import *


from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "identifier",
        "online_status",
        "get_user",
        "home",
        "configured",
        "active",
        "last_seen",
    )

    list_filter = (
        "active",
        "configured",
        "mqtt_profile",
        "home__user",
    )

    search_fields = (
        "identifier",
        "home__user__username",
        "home__user__email",
        "home__name",
    )

    readonly_fields = ("last_seen",)

    # ⚡ Performance-Turbo: Verhindert N+1-Queries in der Admin-Liste
    select_related = ("home__user", "mqtt_profile")

    @admin.display(ordering="home__user", description="User")
    def get_user(self, obj):
        if obj.home and obj.home.user:
            return obj.home.user.email or obj.home.user.username
        return "-"

    @admin.display(description="Status")
    def online_status(self, obj):
        if not obj.last_seen:
            return format_html('<span style="color: #9CA3AF;">⚪ Nie gesehen</span>')
        age = timezone.now() - obj.last_seen
        if age < timedelta(minutes=15):
            return format_html('<span style="color: #10B981; font-weight: bold;">🟢 Online</span>')
        elif age < timedelta(hours=24):
            return format_html('<span style="color: #F59E0B;">🟡 Vor {} Min.</span>', int(age.total_seconds() // 60))
        else:
            return format_html('<span style="color: #EF4444;">🔴 Offline ({} T.)</span>', int(age.days))

@admin.register(DeviceConfig)
class DeviceConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "device",
        "name",
        "role",
    )

    list_filter = (
        "role",
        "home",
    )


@admin.register(DeviceMetric)
class DeviceMetricAdmin(admin.ModelAdmin):
    list_display = ("id", "device", "metric_key", "value", "timestamp")


@admin.register(DeviceLatestMetric)
class DeviceLatestMetricAdmin(admin.ModelAdmin):
    list_display = ("device", "metric_key", "value", "unit", "timestamp", "updated_at")
    list_filter = ("metric_key",)
    search_fields = ("device__identifier", "metric_key")
    readonly_fields = ("updated_at",)


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "name",
        "timezone",
        "mqtt_token",
        "mqtt_username",
        "mqtt_provisioned",
    )

    readonly_fields = (
        "mqtt_token",
        "mqtt_username",
    )

    search_fields = (
        "name",
        "user__username",
        "user__email",
        "mqtt_token",
        "mqtt_username",
    )

    list_filter = (
        "timezone",
        "mqtt_provisioned",
    )


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

@admin.register(MQTTProfile)
class MQTTProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "active",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "name",
        "slug",
    )
