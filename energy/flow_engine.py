##########################
# energy/flow_engine.py
##########################


def calculate_energy_flow(signals):
    """
    Calculate energy flow based on aggregated signals.

    Logic:
    1. PV → Load
    2. PV → Battery
    3. PV → Grid
    4. Battery → Load
    5. Grid → Load
    """

    grid = signals.get("grid", {})
    load = signals.get("load", {})
    pv = signals.get("pv", {})
    battery = signals.get("battery", {})

    consumption = load.get("consumption") or 0
    production = pv.get("production") or 0
    grid_import = grid.get("import") or 0
    grid_export = grid.get("export") or 0
    battery_charge = battery.get("charge") or 0
    battery_discharge = battery.get("discharge") or 0

    flow = {
        "pv_to_load": 0,
        "pv_to_battery": 0,
        "pv_to_grid": 0,
        "battery_to_load": 0,
        "grid_to_load": 0,
    }

    # ✅ 1. PV → Load
    pv_to_load = min(production, consumption)
    flow["pv_to_load"] = pv_to_load

    remaining_load = consumption - pv_to_load
    remaining_pv = production - pv_to_load

    # ✅ 2. PV → Battery
    pv_to_battery = min(remaining_pv, battery_charge)
    flow["pv_to_battery"] = pv_to_battery
    remaining_pv -= pv_to_battery

    # ✅ 3. PV → Grid
    flow["pv_to_grid"] = max(remaining_pv, 0)

    # ✅ 4. Battery → Load
    battery_to_load = min(remaining_load, battery_discharge)
    flow["battery_to_load"] = battery_to_load
    remaining_load -= battery_to_load

    # ✅ 5. Grid → Load (Fallback)
    flow["grid_to_load"] = max(remaining_load, 0)

    return flow

