##############################
# forecast/services_physics.py
##############################

from datetime import timedelta, timezone as dt_timezone
from django.utils import timezone


def predict_next_24h_physics_for_tenant(tenant):
    """
    Sehr einfacher Physics-Fallback:
    nutzt historische Werte als Basis und gibt eine naive Prognose zurück.

    Ziel:
    - NIEMALS None zurückgeben
    - stabile fallback Prognose liefern
    """

    from core.models import AggregatedReading


    # ✅ hole letzte Stundenwerte (falls vorhanden)
    rows = list(
        AggregatedReading.objects.filter(tenant=tenant)
        .order_by("-period_start")
        .values("period_start", "value")[:48]
    )

    # ✅ kein Input → leere Liste (kein Crash)
    if not rows:
        return []

    # ✅ sortieren (chronologisch)
    rows = list(reversed(rows))

    # ✅ einfache durchschnittliche Leistung
    values = [float(r["value"] or 0.0) for r in rows]
    avg_value = sum(values) / len(values) if values else 0.0

    # ✅ Startzeit bestimmen
    last_ts = rows[-1]["period_start"]

    if timezone.is_naive(last_ts):
        last_ts = timezone.make_aware(last_ts, dt_timezone.utc)

    start_ts = last_ts.replace(minute=0, second=0, microsecond=0)

    # ✅ Prognose bauen (24h)
    results = []

    for i in range(24):
        ts = start_ts + timedelta(hours=i + 1)

        # einfacher Verlauf: konstant durchschnitt
        results.append(
            {
                "timestamp": ts,
                "forecast_kw": max(0.0, avg_value),
                "radiation_wm2": None,
                "temperature_c": None,
                "cloud_cover_pct": None,
            }
        )

    return results
