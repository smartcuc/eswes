#############################
# integrations/serializers.py
#############################

from rest_framework import serializers
from .models import InboundWebhookEvent


class InboundWebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboundWebhookEvent
        fields = [
            "id",
            "tenant",
            "event_type",
            "status",
            "received_at",
            "processed_at",
            "error_message",
        ]
