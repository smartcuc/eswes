#######################
# integrations/views.py
#######################
import logging

logger = logging.getLogger(__name__)
logger.info("webhook.accepted")

import hmac
import hashlib

from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Tenant
from integrations.models import InboundWebhookEvent
from integrations.serializers import InboundWebhookEventSerializer
from integrations.tasks import process_inbound_webhook_event

import traceback


def verify_hmac_sha256(request) -> bool:
    """
    GitHub-Style HMAC:
    Header: X-Hub-Signature-256: "sha256=<hex_digest>"
    Digest wird über request.body (raw bytes) gebildet.
    """
    secret = getattr(settings, "WEBHOOK_SECRET", "")
    if not secret:
        return False

    sig = request.headers.get("X-Hub-Signature-256", "")
    if not sig.startswith("sha256="):
        return False

    their_digest = sig.split("=", 1)[1].strip()
    body = request.body  # raw bytes

    our_digest = hmac.new(
        key=secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256
    ).hexdigest()

    # Debug optional:
    if getattr(settings, "DEBUG", False):
        print("OUR DIGEST:", our_digest)
        print("THEIR DIGEST:", their_digest)

    return hmac.compare_digest(our_digest, their_digest)


@api_view(["POST"])
@permission_classes([AllowAny])
def ingest_readings(request):
    #    if not verify_hmac_sha256(request):
    #        return Response({"detail": "invalid signature"}, status=401)

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

    # ✅ NUR speichern + enqueue
    with transaction.atomic():
        evt = InboundWebhookEvent.objects.create(
            tenant=tenant,
            event_type="METER_READING_BATCH",
            payload=payload,
            signature_valid=True,
            status=InboundWebhookEvent.Status.OK,
        )

        transaction.on_commit(lambda: process_inbound_webhook_event.delay(str(evt.id)))

    return Response({"status": "accepted", "event_id": str(evt.id)})


class EventListView(APIView):
    def get(self, request):
        status_filter = request.GET.get("status")

        qs = InboundWebhookEvent.objects.all().order_by("-received_at")

        if status_filter:
            qs = qs.filter(status=status_filter)

        serializer = InboundWebhookEventSerializer(qs, many=True)
        return Response(serializer.data)
