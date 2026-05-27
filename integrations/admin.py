#############################
# integrations/admin.py
#############################

from django.contrib import admin
from .models import InboundWebhookEvent, ApiClient
from integrations.tasks import process_inbound_webhook_event


@admin.register(InboundWebhookEvent)
class InboundWebhookEventAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "tenant",
        "event_type",
        "status",
        "received_at",
        "processed_at",
    )

    list_filter = ("status", "event_type", "tenant")
    search_fields = ("id", "error_message")
    readonly_fields = ("received_at", "processed_at", "payload")
    ordering = ("-received_at",)

    actions = ["replay_events"]

    def replay_events(self, request, queryset):
        for evt in queryset:
            process_inbound_webhook_event.delay(str(evt.id))


@admin.register(ApiClient)
class ApiClientAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "is_active", "created_at")
