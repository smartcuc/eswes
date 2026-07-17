#####################
# market/api/views.py
#####################

from zoneinfo import ZoneInfo

from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from market.models import SpotPrice
from market.services import get_current_spot_price


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_spot_price(request):

    home = request.user.homes.first()

    timezone_name = home.timezone if home and home.timezone else "Europe/Berlin"

    data = get_current_spot_price(timezone_name)

    if not data:
        return Response(
            {"detail": "no price found"},
            status=404,
        )

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def spot_price_chart(request):

    home = request.user.homes.first()

    timezone_name = home.timezone if home and home.timezone else "Europe/Berlin"

    tz = ZoneInfo(timezone_name)

    # DEBUG:
    # Noch NICHT auf heute filtern.
    # Erst prüfen was tatsächlich gespeichert ist.
    rows = SpotPrice.objects.order_by("timestamp")

    prices = [
        round(
            float(row.price_eur_per_kwh) * 100,
            3,
        )
        for row in rows
    ]

    current = prices[-1] if prices else None

    min_price = min(prices) if prices else None

    max_price = max(prices) if prices else None

    avg_price = (
        round(
            sum(prices) / len(prices),
            2,
        )
        if prices
        else None
    )

    return Response(
        {
            "count": rows.count(),
            "first_timestamp": (
                rows.first().timestamp.astimezone(tz).isoformat()
                if rows.exists()
                else None
            ),
            "last_timestamp": (
                rows.last().timestamp.astimezone(tz).isoformat()
                if rows.exists()
                else None
            ),
            "timestamps": [
                row.timestamp.astimezone(tz).strftime("%d.%m %H:%M") for row in rows
            ],
            "values": prices,
            "current": current,
            "min": min_price,
            "max": max_price,
            "avg": avg_price,
        }
    )
