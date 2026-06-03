from rest_framework.decorators import api_view
from rest_framework.response import Response
from billing.models import UserBalanceSlot


@api_view(["GET"])
def consumption_view(request):
    qs = UserBalanceSlot.objects.order_by("period_start")[:100]

    data = [
        {
            "period_start": obj.period_start.isoformat(),
            "consumption_kwh": float(obj.consumption_kwh),
        }
        for obj in qs
    ]

    return Response(data)
