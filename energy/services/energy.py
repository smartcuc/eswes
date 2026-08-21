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

    # 5. Device-IDs fuer die Dashboard-Historiencharts sammeln (Batch-Abfrage)
    sources = list(
        EMSSignalSource.objects.filter(
            home__user=user,
        ).select_related("signal_type")
    )

    from devices.models import Device
    all_user_devices = list(
        Device.objects.filter(
            home__user=user,
            active=True,
            pending_delete=False,
        ).select_related("config__role", "config__generator_type", "config__energy_signal_type")
    )

    grid_ids = {src.device_id for src in sources if src.signal_type and src.signal_type.key in ["grid", "grid_feed_in", "grid_import"]}
    pv_ids = {src.device_id for src in sources if src.signal_type and src.signal_type.key in ["pv", "solar", "producer"]}
    battery_ids = {src.device_id for src in sources if src.signal_type and src.signal_type.key in ["battery", "storage", "speicher"]}
    load_ids = {src.device_id for src in sources if src.signal_type and src.signal_type.key in ["load", "consumer", "consumption"]}

    for dev in all_user_devices:
        cfg = getattr(dev, "config", None)
        if not cfg:
            continue
        sig_key = cfg.energy_signal_type.key if cfg.energy_signal_type else None
        gen_key = cfg.generator_type.key if cfg.generator_type else None
        role_key = cfg.role.key if cfg.role else None

        if sig_key in ["battery", "storage", "speicher"] or gen_key in ["battery", "storage", "speicher"] or role_key in ["battery", "storage", "speicher"]:
            battery_ids.add(dev.id)
        elif sig_key in ["pv", "solar", "producer"] or gen_key in ["pv", "solar"] or (role_key in ["producer", "pv"] and gen_key not in ["battery", "storage", "speicher", "grid"]):
            pv_ids.add(dev.id)
        elif sig_key in ["grid", "grid_feed_in"] or gen_key == "grid" or role_key == "grid":
            grid_ids.add(dev.id)
        elif sig_key in ["load", "consumer", "consumption"] or role_key == "consumer":
            load_ids.add(dev.id)

    battery_net = (battery.get("discharge") or 0) - (battery.get("charge") or 0)

    kpis = {
        "load": round(house_demand, 2),
        "tracked_load": load.get("consumption", 0),
        "pv": pv.get("production", 0),
        "grid": grid.get("import", 0) - grid.get("export", 0),
        "battery": round(battery_net, 2),
        "battery_discharge": battery.get("discharge", 0),
        "battery_charge": battery.get("charge", 0),
        "today": today["value"] if today else 0,
        "today_source": today["source"] if today else None,
    }

    charts = {
        "load": get_house_demand_chart(
            list(pv_ids),
            list(grid_ids),
            list(battery_ids),
        ),
        "pv": get_dashboard_chart(list(pv_ids)),
        "grid": get_dashboard_chart(list(grid_ids)),
        "battery": get_dashboard_chart(list(battery_ids)),
        "today": today["history"] if today else [],
    }

    has_grid = len(grid_ids) > 0
    has_load = load.get("consumption") is not None
    ready = has_grid or len(all_user_devices) > 0

    return {
        # Wenn dein Frontend hier strikt nach Rollen verlangt, 
        # schalte es testweise fest auf True, um zu sehen, ob das Sankey-Diagramm rendert:
        "ready": ready, # oder: has_producer and has_consumer
        "sankey": sankey,
        "kpis": kpis,
        "charts": charts,
    }
