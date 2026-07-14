#####################################
# demo/services/metric_replication.py
#####################################

import logging
from django.utils import timezone
from devices.models import DeviceMetric
from demo.models import DemoDeviceMap
from django.core.cache import cache

SYNC_CACHE_KEY = "demo:last_metric_id"
logger = logging.getLogger(__name__)


def sync_new_metrics():
    """
    Repliziert neue Metriken präzise und blockweise (Bulk) ohne Cache-Zerstörung.
    """
    # 1. Alle Mappings in den RAM laden (source_id -> demo_id)
    mappings = {
        m.source_device_id: m.demo_device_id for m in DemoDeviceMap.objects.all()
    }

    if not mappings:
        logger.info("Keine Demo-Geräte-Mappings konfiguriert.")
        return 0

    source_ids = list(mappings.keys())
    last_metric_id = cache.get(SYNC_CACHE_KEY, 0)

    # 2. Neue Metriken holen (Limitiert auf 1.000 für absolute Präzision)
    new_metrics = list(
        DeviceMetric.objects.filter(
            device_id__in=source_ids, id__gt=last_metric_id
        ).order_by("id")[:1000]
    )

    if not new_metrics:
        return 0

    # 3. Alle relevanten Zeitstempel exakt sammeln (Kein ungenaues Min/Max-Fenster mehr!)
    timestamps = [m.timestamp for m in new_metrics]
    demo_device_ids = list(mappings.values())

    # Vorhandene Datensätze für exakt diese Zeitstempel ermitteln
    existing_pairs = set(
        DeviceMetric.objects.filter(
            device_id__in=demo_device_ids, timestamp__in=timestamps
        ).values_list("device_id", "metric_key", "timestamp")
    )

    # 4. Daten im RAM aufbereiten
    to_create = []
    highest_id = last_metric_id

    for metric in new_metrics:
        if metric.id > highest_id:
            highest_id = metric.id

        demo_device_id = mappings.get(metric.device_id)
        if not demo_device_id:
            continue

        # Validierung: Wenn der Wert null/None ist oder wichtige Felder fehlen, überspringen
        if metric.value is None:
            continue

        # Präziser Dubletten-Check im RAM
        check_key = (demo_device_id, metric.metric_key, metric.timestamp)
        if check_key in existing_pairs:
            continue

        # Objekt sauber bestücken (Wichtig: alle Felder mitnehmen!)
        to_create.append(
            DeviceMetric(
                device_id=demo_device_id,
                metric_key=metric.metric_key,
                unit=metric.unit if metric.unit else "",
                value=metric.value,
                data=metric.data if metric.data else {},
                timestamp=metric.timestamp,
            )
        )

    # 5. Bulk-Insert ausführen
    replicated = 0
    if to_create:
        DeviceMetric.objects.bulk_create(to_create, batch_size=500)
        replicated = len(to_create)

        # 🔥 FEHLERBEHEBUNG CACHE: Invalidiere den Dashboard-Cache für Demo-User,
        # damit das Frontend nicht mehr im 3-Sekunden-Takt "Cache Misses" triggert.
        # Falls du ein spezifisches Cache-Key-Muster für das Dashboard nutzt, hier löschen:
        # cache.delete_pattern("default:device_dashboard:*")

    # Cache für die höchste ID aktualisieren
    if highest_id > last_metric_id:
        cache.set(SYNC_CACHE_KEY, highest_id, None)

    logger.info(
        "Erfolgreich %s Metriken präzise repliziert. (Höchste ID: %s)",
        replicated,
        highest_id,
    )
    return replicated
