#################
# market/admin.py
#################


from django.contrib import admin
from .models import SpotPrice
from market.models_tariff import HomeTariff
from market.models_price_config import ElectricityPriceConfig
from market.models_analysis import SpotPriceDaySummary

@admin.register(SpotPrice)
class SpotPriceAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "price_eur_per_kwh", "source", "created_at")
    list_filter = ("source",)
    search_fields = ("source",)


@admin.register(HomeTariff)
class HomeTariffAdmin(admin.ModelAdmin):

    list_display = (
        "home",
        "tariff_type",
        "valid_from",
        "static_price_eur_per_kwh",
    )

    ordering = ("-valid_from",)


@admin.register(ElectricityPriceConfig)
class ElectricityPriceConfigAdmin(admin.ModelAdmin):

    list_display = (
        "valid_from",
        "grid_fee_ct",
        "vat_percent",
    )

    ordering = ("-valid_from",)


@admin.register(SpotPriceDaySummary)
class SpotPriceDaySummaryAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "cheapest_hour",
        "cheapest_hour_price",
        "best_2h_start",
        "best_3h_start",
        "best_5h_start",
    )

    ordering = ("-date",)

    search_fields = ("date",)
