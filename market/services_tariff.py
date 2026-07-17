###########################
# market/services_tariff.py
###########################

from decimal import Decimal

from market.models_tariff import HomeTariff
from market.models_price_config import (
    ElectricityPriceConfig,
)


def get_home_tariff(
    home,
    date,
):

    return (
        HomeTariff.objects.filter(
            home=home,
            valid_from__lte=date,
        )
        .order_by("-valid_from")
        .first()
    )


def get_price_config(
    date,
):

    return (
        ElectricityPriceConfig.objects.filter(
            valid_from__lte=date,
        )
        .order_by("-valid_from")
        .first()
    )


def calculate_effective_price(
    home,
    timestamp,
    spot_price_ct,
):
    """
    Liefert den tatsächlichen Strompreis
    in ct/kWh.
    """

    tariff = get_home_tariff(
        home,
        timestamp.date(),
    )

    if not tariff:
        return float(spot_price_ct)

    #
    # Fester Tarif
    #
    if tariff.tariff_type == HomeTariff.TARIFF_STATIC:

        return round(
            float(tariff.static_price_eur_per_kwh) * 100,
            2,
        )

    #
    # Dynamischer Tarif
    #
    config = get_price_config(
        timestamp.date(),
    )

    if not config:
        return float(spot_price_ct)

    netto = (
        Decimal(str(spot_price_ct))
        + config.grid_fee_ct
        + config.electricity_tax_ct
        + config.concession_fee_ct
        + config.kwk_levy_ct
        + config.special_grid_levy_ct
        + config.offshore_levy_ct
    )

    brutto = netto * (Decimal("1") + (config.vat_percent / Decimal("100")))

    return round(
        float(brutto),
        2,
    )
