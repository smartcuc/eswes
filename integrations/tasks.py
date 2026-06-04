##########################
# integrations/tasks.py
##########################

from celery import shared_task
from django.db import connection

from metering.models import Meter
from integrations.services_tibber import upsert_tibber_interval_readings


def insert_interval_reading(data):
    sql = """
    INSERT INTO metering_intervalreading (
        id,
        meter_id,
        ts_start,
        obis_code,
        value,
        unit,
        source,
        created_at,
        received_at,
        is_late,
        is_duplicate
    )
    VALUES (
        gen_random_uuid(),
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        now(),
        now(),
        false,
        false
    )
    ON CONFLICT DO NOTHING;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            sql,
            [
                data["meter_id"],
                data["ts_start"],
                data["obis_code"],
                data["value"],
                data.get("unit", "kWh"),
                data.get("source", "api"),
            ],
        )


from celery import shared_task
from metering.models import Meter
from integrations.services_tibber import upsert_tibber_interval_readings


@shared_task
def sync_tibber():
    print("INFO: Tibber Sync aktuell deaktiviert – Live Pipeline aktiv")
    return 0


"""     print("🔥 SYNC RUNNING")

    from metering.models import Meter
    from integrations.services_tibber import upsert_tibber_interval_readings

    meters = Meter.objects.all()

    total = 0

    # ✅ NUR Tibber Meter (optional wenn du später andere Quellen hast)
    # if meter.integration_type != "tibber":
    #     continue

    for meter in meters:
        #     # ✅ NUR Tibber Meter
        #     if meter.integration_type != "tibber":
        #         continue

        #     # ✅ NUR wenn Pulse vorhanden
        #     if not getattr(meter, "has_tibber_pulse", False):
        #         print("SKIP: no Tibber Pulse")
        #         continue

        # ✅ EINZIGE WAHRHEIT: data_resolution
        if meter.data_resolution != "quarter_hourly":
            print("SKIP: keine 15min Daten")
            continue

        # ✅ MUSS vorhanden sein
        if not meter.tibber_home_id:
            print("SKIP: no home_id")
            continue

        print("SYNC meter:", meter.id)

        result = upsert_tibber_interval_readings(
            meter=meter,
            home_id=meter.tibber_home_id,
            user=meter.owner_user,
            hours=24,
        )

        print("RESULT:", result)

        total += result.get("written", 0)

    print("✅ TOTAL WRITTEN:", total)

    return total
 """


@shared_task
def flush_live_slots_task():
    from integrations.live_energy_pipeline import flush_ready_slots

    flush_ready_slots()


@shared_task
def process_inbound_webhook_event(payload):
    insert_interval_reading(payload)
    return "ok"
