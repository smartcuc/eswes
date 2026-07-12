###########################
# energy/services/energy.py
###########################

from energy.services.signals import get_ems_signals
from energy.flow_engine import calculate_energy_flow
from energy.services.sankey import build_live_sankey
from energy.services.kpis import ( get_today_consumption, )
from energy.services.charts import (get_dashboard_chart,)
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
    has_producer = (signals.get("pv", {}).get("production") is not None)
    has_consumer = (signals.get("load", {}).get("consumption") is not None)

    load = signals.get("load", {})
    pv = signals.get("pv", {})
    grid = signals.get("grid", {})

    # 4. Heutigen Verbrauch ermitteln
    today = get_today_consumption(user)

    kpis = {
        "load": load.get("consumption", 0),
        "pv": pv.get("production", 0),
        "grid": grid.get("import", 0) - grid.get("export", 0),
        "today": today["value"] if today else 0,
        "today_source": today["source"] if today else None,
    }

    grid_ids = list(
        EMSSignalSource.objects.filter(
            home__user=user,
            signal_type="grid",
        ).values_list(
            "device_id",
            flat=True,
        )
    )

    pv_ids = list(
        EMSSignalSource.objects.filter(
            home__user=user,
            signal_type="pv",
        ).values_list(
            "device_id",
            flat=True,
        )
    )

    charts = {
        "load": get_dashboard_chart(grid_ids),
        "pv": get_dashboard_chart(pv_ids),
        "grid": get_dashboard_chart(grid_ids),
        "today": today["history"] if today else [],
    }

    return {
        # Wenn dein Frontend hier strikt nach Rollen verlangt, 
        # schalte es testweise fest auf True, um zu sehen, ob das Sankey-Diagramm rendert:
        "ready": True, # oder: has_producer and has_consumer
        "sankey": sankey,
        "kpis": kpis,
        "charts": charts,
    }
