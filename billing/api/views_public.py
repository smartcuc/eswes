#############################
# billing/api/views_public.py
#############################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from billing.models import UserBalanceSlot


@api_view(["GET"])
@permission_classes([AllowAny])
def public_consumption_view(request):

    qs = UserBalanceSlot.objects.order_by("period_start")[:100]

    data = [
        {
            "period_start": obj.period_start.isoformat(),
            "consumption_kwh": float(obj.consumption_kwh),
        }
        for obj in qs
    ]

    return Response(data)
