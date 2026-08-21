##########################
# energy/flow_engine.py
##########################

def calculate_energy_flow(signals):
    """
    Enterprise-Grade Energy Flow Balancing Engine.

    Physische Verteilung:
    1. PV → Hauslast (Eigenverbrauch zuerst)
    2. PV → Batterie (Überschussladung)
    3. PV → Netz (Netzeinspeisung)
    4. Batterie → Hauslast (Entladung bei PV-Defizit)
    5. Netz → Hauslast (Netzbezug bei Restlast)
    6. Netz → Batterie (optional bei dynamischen Tarifen / Grid-Charging)

    Liefert alle Kanten-Werte in Watt (W) sowie berechnete KPIs (Autarkie, Eigenverbrauchsquote).
    """
    signals = signals or {}

    grid = signals.get("grid", {})
    load = signals.get("load", {})
    pv = signals.get("pv", {})
    battery = signals.get("battery", {})

    production = float(pv.get("production") or 0)
    battery_charge = float(battery.get("charge") or 0)
    battery_discharge = float(battery.get("discharge") or 0)
    grid_import = float(grid.get("import") or 0)
    grid_export = float(grid.get("export") or 0)
    consumption = float(load.get("consumption") or 0)

    # ✅ Falls Gesamtverbrauch nicht direkt gemessen wird, physikalisch bilanzieren:
    # Supply = Production + Grid Import + Battery Discharge
    # Destination = Consumption + Grid Export + Battery Charge
    if consumption <= 0 and (production > 0 or grid_import > 0 or battery_discharge > 0):
        derived_consumption = (
            production + grid_import + battery_discharge - grid_export - battery_charge
        )
        consumption = max(0.0, derived_consumption)

    flow = {
        "pv_to_load": 0.0,
        "pv_to_battery": 0.0,
        "pv_to_grid": 0.0,
        "battery_to_load": 0.0,
        "grid_to_load": 0.0,
        "grid_to_battery": 0.0,
        "total_consumption": consumption,
        "total_production": production,
    }

    # 1. PV → Hauslast (Direktverbrauch)
    pv_to_load = min(production, consumption)
    flow["pv_to_load"] = pv_to_load

    remaining_load = max(0.0, consumption - pv_to_load)
    remaining_pv = max(0.0, production - pv_to_load)

    # 2. PV → Batterie (Überschussladung)
    if battery_charge > 0 and remaining_pv > 0:
        pv_to_battery = min(remaining_pv, battery_charge)
        flow["pv_to_battery"] = pv_to_battery
        remaining_pv = max(0.0, remaining_pv - pv_to_battery)

    # 3. PV → Netz (Netzeinspeisung)
    if grid_export > 0:
        flow["pv_to_grid"] = min(remaining_pv, grid_export) if remaining_pv > 0 else grid_export
    else:
        flow["pv_to_grid"] = max(0.0, remaining_pv)

    # 4. Batterie → Hauslast (Defizitausgleich)
    if battery_discharge > 0 and remaining_load > 0:
        battery_to_load = min(remaining_load, battery_discharge)
        flow["battery_to_load"] = battery_to_load
        remaining_load = max(0.0, remaining_load - battery_to_load)

    # 5. Netz → Hauslast (Netzbezug für verbleibende Last)
    if grid_import > 0:
        flow["grid_to_load"] = min(remaining_load, grid_import) if remaining_load > 0 else grid_import
    else:
        flow["grid_to_load"] = max(0.0, remaining_load)

    # 6. Netz → Batterie (z. B. Smart Grid Charging bei günstigen Börsenpreisen)
    if battery_charge > flow["pv_to_battery"]:
        flow["grid_to_battery"] = battery_charge - flow["pv_to_battery"]

    # ✅ KPI Quoten berechnen
    self_consumption_watts = flow["pv_to_load"] + flow["pv_to_battery"]
    flow["self_consumption_rate"] = (
        (self_consumption_watts / production * 100.0) if production > 0 else 100.0
    )
    autarky_watts = flow["pv_to_load"] + flow["battery_to_load"]
    flow["autarky_rate"] = (
        (autarky_watts / consumption * 100.0) if consumption > 0 else (100.0 if production > 0 else 0.0)
    )

    return flow


