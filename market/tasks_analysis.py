##########################
# market/tasks_analysis.py
##########################

from celery import shared_task
from django.utils import timezone

from market.models_analysis import SpotPriceDaySummary
from market.services_price_analysis import get_price_insights


@shared_task
def compute_daily_spot_summary():

    insights = get_price_insights()

    today = timezone.now().date()

    if not insights or not insights.get("cheapest_hours"):
        return

    cheapest = insights["cheapest_hours"][0]

    SpotPriceDaySummary.objects.update_or_create(
        date=today,
        defaults={
            "cheapest_hour": cheapest["hour"],
            "cheapest_hour_price": cheapest["price"],
            "best_2h_start": insights["best_2h"]["start"],
            "best_2h_price": insights["best_2h"]["avg_price"],
            "best_3h_start": insights["best_3h"]["start"],
            "best_3h_price": insights["best_3h"]["avg_price"],
            "best_5h_start": insights["best_5h"]["start"],
            "best_5h_price": insights["best_5h"]["avg_price"],
        },
    )
