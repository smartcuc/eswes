#################
# market/admin.py
#################


from django.contrib import admin
from .models import SpotPrice
from market.models_tariff import HomeTariff
from market.models_price_config import ElectricityPriceConfig

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
