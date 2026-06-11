#
# billing/services.py
#


def calculate_energy_balance(tenant, ts_start):

    from core.models import AggregatedReading

    readings = AggregatedReading.objects.filter(
        tenant=tenant, period_type="15min", period_start=ts_start
    )

    consumption = 0
    generation = 0

    for r in readings:
        if r.obis_code.startswith("1.8"):
            consumption += r.value
        elif r.obis_code.startswith("2.8"):
            generation += r.value

    # ✅ interne Deckung
    internal = min(consumption, generation)

    # ✅ Rest Netzbezug
    grid_import = max(consumption - internal, 0)

    # ✅ Rest Einspeisung
    grid_export = max(generation - internal, 0)

    return {
        "consumption": consumption,
        "generation": generation,
        "internal": internal,
        "grid_import": grid_import,
        "grid_export": grid_export,
    }
