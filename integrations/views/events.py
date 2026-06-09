##############################
# integrations/views/events.py
##############################


from rest_framework.views import APIView
from rest_framework.response import Response

from integrations.models import InboundWebhookEvent
from integrations.serializers import InboundWebhookEventSerializer


class EventListView(APIView):
    def get(self, request):
        status_filter = request.GET.get("status")

        qs = InboundWebhookEvent.objects.all().order_by("-received_at")

        if status_filter:
            qs = qs.filter(status=status_filter)

        serializer = InboundWebhookEventSerializer(qs, many=True)
        return Response(serializer.data)
    