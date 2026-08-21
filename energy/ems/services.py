########################
# energy/ems/services.py
########################

from devices.models import Device
from devices.services.metrics import get_latest_values
from energy.models import EMSSignalSource


def build_device_signals(user):
    signals = {
        "grid": {"import": 0, "export": 0},
        "load": {"consumption": None},
        "pv": {"production": 0},
        "battery": {"charge": 0, "discharge": 0},
    }

    # 1. Holt alle konfigurierten Geräte des Benutzers (1 Query)
    all_devices = list(
        Device.objects.filter(
            home__user=user,
            active=True,
            pending_delete=False,
        ).select_related(
            "config__role",
            "config__generator_type",
            "config__energy_signal_type",
        )
    )

    values = get_latest_values([device.id for device in all_devices])

    # 2. Explizite EMS-Signalquellen aus der DB holen
    sources = list(
        EMSSignalSource.objects.filter(
            home__user=user,
        ).select_related("signal_type")
    )

    pv_device_ids = {
        src.device_id for src in sources
        if src.signal_type and src.signal_type.key in ["pv", "solar", "producer"]
    }
    grid_device_ids = {
        src.device_id for src in sources
        if src.signal_type and src.signal_type.key in ["grid", "grid_feed_in", "grid_import"]
    }
    battery_device_ids = {
        src.device_id for src in sources
        if src.signal_type and src.signal_type.key in ["battery", "storage", "speicher"]
    }
    load_device_ids = {
        src.device_id for src in sources
        if src.signal_type and src.signal_type.key in ["load", "consumer", "consumption"]
    }

    # 3. Fallback: Nur wenn fuer einen Signal-Typ KEINE explizite EMS-Signalquelle existiert
    for dev in all_devices:
        cfg = getattr(dev, "config", None)
        if not cfg:
            continue

        sig_key = cfg.energy_signal_type.key if cfg.energy_signal_type else None
        role_key = cfg.role.key if cfg.role else None

        # Batterie (nur falls noch keine Batterie-Source definiert)
        if not battery_device_ids and (
            sig_key in ["battery", "storage", "speicher"]
            or role_key in ["battery", "storage", "speicher"]
        ):
            battery_device_ids.add(dev.id)

        # PV (nur falls noch keine PV-Source definiert)
        if not pv_device_ids and (
            sig_key in ["pv", "solar", "producer"]
            or (role_key in ["producer", "pv"])
        ):
            pv_device_ids.add(dev.id)

        # Netz (nur falls noch keine Grid-Source definiert)
        if not grid_device_ids and (
            sig_key in ["grid", "grid_feed_in", "grid_import"]
            or role_key == "grid"
        ):
            grid_device_ids.add(dev.id)

        # Last (nur falls noch keine Load-Source definiert)
        if not load_device_ids and (
            sig_key in ["load", "consumer", "consumption"]
            or role_key == "consumer"
        ):
            load_device_ids.add(dev.id)

    # 4. PV-Erzeugung berechnen
    pv_power = sum(max(values.get(d_id, 0), 0) for d_id in pv_device_ids)
    signals["pv"]["production"] = pv_power

    # 5. Grid-Leistung (Import / Export)
    grid_power = sum(values.get(d_id, 0) for d_id in grid_device_ids)
    if grid_power >= 0:
        signals["grid"]["import"] = grid_power
        signals["grid"]["export"] = 0
    else:
        signals["grid"]["import"] = 0
        signals["grid"]["export"] = abs(grid_power)

    # 6. Batterie-Leistung (Discharge / Charge)
    # Bei Batteriespeichern gilt:
    # Entladen (Strom fließt ins Haus): positiv
    # Laden (Strom fließt in den Speicher): negativ (bzw. abs)
    battery_power = sum(values.get(d_id, 0) for d_id in battery_device_ids)
    if battery_power >= 0:
        signals["battery"]["discharge"] = battery_power
        signals["battery"]["charge"] = 0
    else:
        signals["battery"]["discharge"] = 0
        signals["battery"]["charge"] = abs(battery_power)

    # 7. Last (Hausverbrauch)
    tracked_load_devs = [
        d_id for d_id in load_device_ids
        if d_id not in grid_device_ids and d_id not in pv_device_ids and d_id not in battery_device_ids
    ]
    load_power = sum(max(values.get(d_id, 0), 0) for d_id in tracked_load_devs)

    if load_device_ids:
        signals["load"]["consumption"] = load_power
    else:
        # Physikalische Bilanzierung: PV + Batterie-Entladung + Netz-Bezug - Batterie-Ladung - Netz-Einspeisung
        derived = (
            signals["pv"]["production"]
            + signals["battery"]["discharge"]
            + signals["grid"]["import"]
            - signals["battery"]["charge"]
            - signals["grid"]["export"]
        )
        signals["load"]["consumption"] = max(derived, 0)

    return signals
