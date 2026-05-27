##################
# metering/obis.py
##################

OBIS_MAP = {
    # ✅ Energie Bezug
    "1.8.0": {"name": "Verbrauch total", "unit": "kWh", "type": "energy_import"},
    "1.8.1": {"name": "Verbrauch Tarif 1", "unit": "kWh", "type": "energy_import"},
    "1.8.2": {"name": "Verbrauch Tarif 2", "unit": "kWh", "type": "energy_import"},
    # ✅ Energie Einspeisung
    "2.8.0": {"name": "Einspeisung total", "unit": "kWh", "type": "energy_export"},
    # ✅ Leistung (Realtime)
    "16.7.0": {"name": "Momentanleistung", "unit": "W", "type": "power"},
    "36.7.0": {"name": "Leistung L1", "unit": "W", "type": "power"},
    "56.7.0": {"name": "Leistung L2", "unit": "W", "type": "power"},
    "76.7.0": {"name": "Leistung L3", "unit": "W", "type": "power"},
}
