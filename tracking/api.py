#################
# tracking/api.py
#################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import track_event
from .analytics import get_kpis, get_funnel


class TrackEventView(APIView):
    def post(self, request):
        name = request.data.get("name")
        metadata = request.data.get("metadata", {})

        track_event(name=name, metadata=metadata, request=request)

        return Response({"ok": True})


class TrackEventBatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        events = request.data.get("events", [])

        for e in events:
            track_event(
                name=e.get("name"),
                metadata=e.get("metadata", {}),
                request=request,
            )

        return Response({"ok": True})


class KPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = getattr(request.user, "tenant", None)

        return Response(get_kpis(tenant=tenant, context="tenant"))


class FunnelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = getattr(request.user, "tenant", None)

        return Response(get_funnel(tenant=tenant, context="tenant"))