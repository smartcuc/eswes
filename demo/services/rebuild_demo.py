###############################
# demo/services/rebuild_demo.py
###############################

from demo.models import DemoDeviceMap

from django.contrib.auth import get_user_model

from devices.models import (
    Home,
    Device,
    DeviceConfig,
)

from energy.ems.models import (
    EMSSignalSource,
)

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

    # Demo komplett zurücksetzen
    demo_user.homes.all().delete()

    # Neues Demo Home
    demo_home = Home.objects.create(
        user=demo_user,
        name=source_home.name,
        timezone=source_home.timezone,
    )

    device_map = {}

    # Devices
    for device in source_home.devices.all():

        new_device = Device.objects.create(
            home=demo_home,
            identifier=device.identifier,
            mqtt_profile=device.mqtt_profile,
            configured=device.configured,
            active=device.active,
        )

        device_map[device.id] = new_device

        DemoDeviceMap.objects.create(
            source_device=device,
            demo_device=new_device,
        )

        if hasattr(device, "config"):

            cfg = device.config

            DeviceConfig.objects.create(
                device=new_device,
                name=cfg.name,
                role=cfg.role,
                measurement_type=cfg.measurement_type,
                home=demo_home,
                floor=cfg.floor,
                room=cfg.room,
            )

    # EMS
    for src in EMSSignalSource.objects.filter(home=source_home):

        EMSSignalSource.objects.create(
            home=demo_home,
            device=device_map[src.device_id],
            signal_type=src.signal_type,
        )

    return {
        "devices": demo_home.devices.count(),
        "home": demo_home.id,
    }
