###########################
# energy/services/energy.py
###########################

from energy.services.signals import get_ems_signals
from energy.flow_engine import calculate_energy_flow
from energy.services.sankey import build_live_sankey
from energy.services.kpis import get_today_consumption
from energy.services.charts import get_dashboard_chart, get_house_demand_chart
from energy.ems.models import (EMSSignalSource,)

from user_settings.models import UserPreference


def get_energy_data(user):
    # 1. Usereinstellungen laden (Sehr schlank)
    preference, _ = UserPreference.objects.get_or_create(
        user=user,
        key="sankey",
    )
    settings = preference.value or {}
    show_floors = settings.get("showFloors", True)
    show_rooms = settings.get("showRooms", True)

    # 2. Signale und Flüsse holen (Jetzt blitzschnell via Redis-Cache!)
    signals = get_ems_signals(user)
    flow = calculate_energy_flow(signals)

    # 3. Sankey-Diagramm generieren
    sankey = build_live_sankey(
        user,
        flow,
        signals,
        show_floors=show_floors,
        show_rooms=show_rooms,
    )

    # 💡 OPTIMIERUNG: "ready"-Check ohne DB-Abfragen!
    # Wir prüfen einfach direkt in den Live-Signalen, ob Werte für Erzeugung (PV)
    # oder Verbrauch (Load) existieren. Das spart 2 schwere SQL-Queries!
    load = signals.get("load", {})
    pv = signals.get("pv", {})
    grid = signals.get("grid", {})
    battery = signals.get("battery", {})

    house_demand = (
        (pv.get("production") or 0)
        + (battery.get("discharge") or 0)
        + (grid.get("import") or 0)
        - (battery.get("charge") or 0)
        - (grid.get("export") or 0)
    )
    # 4. Heutigen Verbrauch ermitteln
    today = get_today_consumption(user)

    kpis = {
        "load": round(house_demand, 2),
        "tracked_load": load.get("consumption", 0),
        "pv": pv.get("production", 0),
        "grid": grid.get("import", 0) - grid.get("export", 0),
        "today": today["value"] if today else 0,
        "today_source": today["source"] if today else None,
    }

    grid_ids = list(
        EMSSignalSource.objects.filter(
            home__user=user,
            signal_type__key="grid",
        ).values_list(
            "device_id",
            flat=True,
        )
    )

    pv_ids = list(
        EMSSignalSource.objects.filter(
            home__user=user,
            signal_type__key="pv",
        ).values_list(
            "device_id",
            flat=True,
        )
    )

    battery_ids = list(
        EMSSignalSource.objects.filter(
            home__user=user,
            signal_type__key="battery",
        ).values_list(
            "device_id",
            flat=True,
        )
    )

    load_ids = list(
        EMSSignalSource.objects.filter(
            home__user=user,
            signal_type__key="load",
        ).values_list(
            "device_id",
            flat=True,
        )
    )

    charts = {
#        "load": get_dashboard_chart(load_ids),
        "load": get_house_demand_chart(
            pv_ids,
            grid_ids,
            battery_ids,
        ),
        "pv": get_dashboard_chart(pv_ids),
        "grid": get_dashboard_chart(grid_ids),
        "today": today["history"] if today else [],
    }

    has_grid = len(grid_ids) > 0
    has_load = load.get("consumption") is not None
    ready = has_grid and has_load

    return {
        # Wenn dein Frontend hier strikt nach Rollen verlangt, 
        # schalte es testweise fest auf True, um zu sehen, ob das Sankey-Diagramm rendert:
        "ready": ready, # oder: has_producer and has_consumer
        "sankey": sankey,
        "kpis": kpis,
        "charts": charts,
    }
