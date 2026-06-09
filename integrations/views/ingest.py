##############################
# integrations/views/ingest.py
##############################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.db import transaction
from core.models import Tenant
from integrations.models import InboundWebhookEvent
from integrations.tasks import process_inbound_webhook_event

import traceback


@api_view(["POST"])
@permission_classes([AllowAny])
def ingest_readings(request):
    payload = request.data
    tenant_id = payload.get("tenant_id")

    if not tenant_id:
        return Response({"detail": "tenant_id missing"}, status=400)

    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        return Response({"detail": "tenant not found"}, status=404)

    except Exception as e:
        print("🔥 ERROR:", str(e))
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)

    with transaction.atomic():
        evt = InboundWebhookEvent.objects.create(
            tenant=tenant,
            event_type="METER_READING_BATCH",
            payload=payload,
            signature_valid=True,
            status=InboundWebhookEvent.Status.OK,
        )

        transaction.on_commit(
            lambda: process_inbound_webhook_event.delay(str(evt.id))
        )

    return Response({"status": "accepted", "event_id": str(evt.id)})
