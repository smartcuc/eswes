from decimal import Decimal
from datetime import datetime, timezone as dt_timezone
from django.test import TestCase
from django.utils import timezone

from market.models import SpotPrice
from market.services_price_analysis import (
    get_hourly_prices,
    get_cheapest_hours,
    find_cheapest_window,
    get_price_insights,
)


class MarketAnalysisTest(TestCase):
    def setUp(self):
        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Create 24 hours of spot prices
        prices = [
            0.15, 0.12, 0.10, 0.08, 0.09, 0.14,
            0.20, 0.25, 0.22, 0.18, 0.15, 0.13,
            0.11, 0.10, 0.09, 0.12, 0.16, 0.24,
            0.28, 0.26, 0.21, 0.17, 0.14, 0.12,
        ]

        objs = []
        for hour, price in enumerate(prices):
            # 4 quarter-hours per hour
            for q in range(4):
                ts = now + timezone.timedelta(hours=hour, minutes=q * 15)
                objs.append(
                    SpotPrice(
                        timestamp=ts,
                        price_eur_per_kwh=Decimal(str(price)),
                        source="energy-charts",
                    )
                )

        SpotPrice.objects.bulk_create(
            objs,
            update_conflicts=True,
            unique_fields=["timestamp", "source"],
            update_fields=["price_eur_per_kwh"],
        )

    def test_get_hourly_prices(self):
        hourly = get_hourly_prices()
        self.assertGreater(len(hourly), 0)
        self.assertIn("hour", hourly[0])
        self.assertIn("price", hourly[0])

    def test_get_cheapest_hours(self):
        hourly = get_hourly_prices()
        cheapest = get_cheapest_hours(hourly)
        self.assertLessEqual(len(cheapest), 3)
        if len(cheapest) >= 2:
            self.assertLessEqual(cheapest[0]["price"], cheapest[1]["price"])

    def test_find_cheapest_window(self):
        hourly = get_hourly_prices()
        best_2h = find_cheapest_window(hourly, 2)
        self.assertIsNotNone(best_2h)
        self.assertIn("start", best_2h)
        self.assertIn("avg_price", best_2h)

    def test_get_price_insights(self):
        insights = get_price_insights()
        self.assertIn("cheapest_hours", insights)
        self.assertIn("best_2h", insights)
        self.assertIn("best_3h", insights)
        self.assertIn("best_5h", insights)
