#####################
# operations/admin.py
#####################

import json
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import HealthState
from .tasks import run_health_checks


@admin.register(HealthState)
class HealthStateAdmin(admin.ModelAdmin):

    list_display = (
        "service_name",
        "status_badge",
        "value",
        "last_checked",
    )

    list_filter = ("status",)
    search_fields = ("key", "value")

    readonly_fields = (
        "key",
        "status",
        "status_badge",
        "value",
        "pretty_details",
        "checked_at",
    )

    actions = ["trigger_health_checks"]

    HUMAN_LABELS = {
        "mqtt": "📡 MQTT Ingress / Telemetrie",
        "active_devices": "⚡ Aktive EMS-Geräte",
        "spot_prices": "📈 EPEX Spot-Preise (Börse)",
        "weather_sync": "☀️ Wetter- & Solar-Prognose",
        "tibber_sync": "🔌 Tibber Zähler-Synchronisation",
        "aggregation_1m": "⏱️ 1m Aggregation",
        "aggregation_5m": "⏱️ 5m Aggregation",
        "aggregation_15m": "⏱️ 15m Aggregation",
        "aggregation_1h": "⏱️ 1h Aggregation",
        "celery_queue_celery": "⚙️ Celery Queue: Default",
        "celery_queue_critical": "🚨 Celery Queue: Critical",
        "celery_queue_market": "📈 Celery Queue: Market",
        "celery_queue_aggregation": "⏱️ Celery Queue: Aggregation",
        "celery_queue_telemetry": "📡 Celery Queue: Telemetry",
        "celery_queue_forecast": "☀️ Celery Queue: Forecast",
    }

    def service_name(self, obj):
        label = self.HUMAN_LABELS.get(obj.key, obj.key)
        return format_html("<b>{}</b><br><small style='color: #6B7280;'>{}</small>", label, obj.key)

    service_name.short_description = "System / Service"

    def status_badge(self, obj):
        if obj.status == "ok":
            bg, fg, icon = "#10B981", "#FFFFFF", "🟢 OK"
        elif obj.status == "warn":
            bg, fg, icon = "#F59E0B", "#FFFFFF", "🟡 WARN"
        else:
            bg, fg, icon = "#EF4444", "#FFFFFF", "🔴 ERROR"

        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
            bg,
            fg,
            icon,
        )

    status_badge.short_description = "Status"

    def last_checked(self, obj):
        if not obj.checked_at:
            return "-"
        age = timezone.now() - obj.checked_at
        mins = int(age.total_seconds() // 60)
        if mins < 1:
            return "Gerade eben"
        elif mins < 60:
            return f"vor {mins} Min."
        else:
            return f"vor {int(mins // 60)} Std."

    last_checked.short_description = "Geprüft"

    def pretty_details(self, obj):
        if not obj.details:
            return "-"
        return format_html("<pre style='background: #1F2937; color: #F9FAFB; padding: 10px; border-radius: 6px;'>{}</pre>", json.dumps(obj.details, indent=2))

    pretty_details.short_description = "Details (JSON)"

    @admin.action(description="⚡ Health-Checks jetzt manuell ausführen")
    def trigger_health_checks(self, request, queryset):
        run_health_checks.delay()
        self.message_user(request, "Health-Checks wurden im Hintergrund gestartet.")
