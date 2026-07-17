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

    range_type = request.GET.get(
        "range",
        "2d",
    )

    home = request.user.homes.first()

    timezone_name = (
        home.timezone
        if home and home.timezone
        else "Europe/Berlin"
    )

    tz = ZoneInfo(timezone_name)

    local_now = timezone.now().astimezone(tz)

    today_start = local_now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    tomorrow_start = (
        today_start
        + timezone.timedelta(days=1)
    )

    day_after_tomorrow = (
        today_start
        + timezone.timedelta(days=2)
    )

    if range_type == "2d":

        start = today_start.astimezone(
            ZoneInfo("UTC")
        )

        end = day_after_tomorrow.astimezone(
            ZoneInfo("UTC")
        )

    elif range_type == "today":

        start = today_start.astimezone(
            ZoneInfo("UTC")
        )

        end = tomorrow_start.astimezone(
            ZoneInfo("UTC")
        )

    elif range_type == "tomorrow":

        start = tomorrow_start.astimezone(
            ZoneInfo("UTC")
        )

        end = day_after_tomorrow.astimezone(
            ZoneInfo("UTC")
        )

    elif range_type == "5d":

        start = (
            today_start
            - timezone.timedelta(days=4)
        ).astimezone(
            ZoneInfo("UTC")
        )

        end = day_after_tomorrow.astimezone(
            ZoneInfo("UTC")
        )

    else:

        start = today_start.astimezone(
            ZoneInfo("UTC")
        )

        end = day_after_tomorrow.astimezone(
            ZoneInfo("UTC")
        )

    rows = (
        SpotPrice.objects
        .filter(
            timestamp__gte=start,
            timestamp__lt=end,
        )
        .order_by("timestamp")
    )

    prices = [
        round(
            float(row.price_eur_per_kwh) * 100,
            3,
        )
        for row in rows
    ]

    current = prices[-1] if prices else None

    min_price = (
        min(prices)
        if prices
        else None
    )

    max_price = (
        max(prices)
        if prices
        else None
    )

    avg_price = (
        round(
            sum(prices) / len(prices),
            2,
        )
        if prices
        else None
    )

    # Aktuelle Viertelstunde bestimmen
    minute = (local_now.minute // 15) * 15

    current_slot = local_now.replace(
        minute=minute,
        second=0,
        microsecond=0,
    )

    return Response(
        {
            "range": range_type,
            "count": rows.count(),
            "now_label": current_slot.strftime("%d.%m %H:%M"),
            "tomorrow_label": tomorrow_start.strftime("%d.%m %H:%M"),
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
