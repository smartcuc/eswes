##################
# devices/admin.py
##################

from django.contrib import admin
from .models import *


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "get_user",       # 💡 Geändert: Nutzt die Methode von unten
        "name", 
        "identifier", 
        "home"
        )

    search_fields = (
        "home__user__username", # 💡 Korrigiert: Sucht im verknüpften User-Modell via Home
        "home__user__email",    # 💡 Bonus: Erlaubt auch die Suche nach der E-Mail des Users
        "identifier"
    )
    
    # ⚡ Performance-Turbo: Verhindert N+1-Queries in der Admin-Liste
    select_related = ("home__user",)

    @admin.display(ordering="home__user", description="User")
    def get_user(self, obj):
        # Holt den User über das verknüpfte Home-Objekt
        if obj.home and obj.home.user:
            return obj.home.user.email or obj.home.user.username
        return "-"

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


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "name",
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


    