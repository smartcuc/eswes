###############################
# demo/services/rebuild_demo.py
###############################

from demo.models import DemoDeviceMap
from django.contrib.auth import get_user_model
from devices.models import Home, Device, DeviceConfig
from energy.ems.models import EMSSignalSource

User = get_user_model()

MASTER_EMAIL = "ruediger.koenen@web.de"
DEMO_EMAIL = "demo@sharegy.de"


def rebuild_demo_environment():
    source_user = User.objects.get(email=MASTER_EMAIL)

    demo_user, _ = User.objects.get_or_create(
        email=DEMO_EMAIL,
        defaults={
            "username": "demo",
            "is_active": True,
        },
    )

    source_home = source_user.homes.first()
    if not source_home:
        raise RuntimeError("Master home not found")

    # 1. Altes Demo-Home komplett löschen (Kaskadiert auch alte Demo-Devices/Configs weg)
    demo_user.homes.all().delete()

    # 2. Neues Demo-Home anlegen
    demo_home = Home.objects.create(
        user=demo_user,
        name=f"{source_home.name} (Demo)",
        timezone=source_home.timezone,
    )

    device_map = {}

    # 3. Devices klonen mit isolierten Identifiers
    for device in source_home.devices.all():

        # ✅ FIX: 'demo_' Präfix verhindert Cache-Konflikte und doppelte DB-Identitäten!
        new_identifier = (
            f"demo_{device.identifier}" if device.identifier else f"demo_{device.id}"
        )

        new_device = Device.objects.create(
            home=demo_home,
            identifier=new_identifier,  # Isoliert
            mqtt_profile=device.mqtt_profile,
            configured=device.configured,
            active=device.active,
        )

        device_map[device.id] = new_device

        # Zuordnung für den späteren Metric-Sync speichern
        DemoDeviceMap.objects.create(
            source_device=device,
            demo_device=new_device,
        )

        # DeviceConfig klonen
        if hasattr(device, "config"):
            cfg = device.config
            DeviceConfig.objects.create(
                device=new_device,
                name=f"{cfg.name} (Demo)",
                role=cfg.role,
                measurement_type=cfg.measurement_type,
                home=demo_home,
                floor=cfg.floor,
                room=cfg.room,
            )

    # 4. EMS Signalquellen klonen
    for src in EMSSignalSource.objects.filter(home=source_home):
        # Nur klonen, wenn das dazugehörige Gerät auch erfolgreich kopiert wurde
        if src.device_id in device_map:
            EMSSignalSource.objects.create(
                home=demo_home,
                device=device_map[src.device_id],
                signal_type=src.signal_type,
            )

    return {
        "devices": demo_home.devices.count(),
        "home": demo_home.id,
    }
