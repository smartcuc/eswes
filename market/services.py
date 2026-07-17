####################
# market/services.py
####################

from zoneinfo import ZoneInfo
from django.utils import timezone
from market.models import SpotPrice


def get_current_spot_price(timezone_name="Europe/Berlin"):

    current = (
        SpotPrice.objects.filter(timestamp__lte=timezone.now())
        .order_by("-timestamp")
        .first()
    )

    if not current:
        return None

    price_ct = round(
        float(current.price_eur_per_kwh) * 100,
        2,
    )

    return {
        "timestamp": current.timestamp,
        "price_ct": price_ct,
    }
