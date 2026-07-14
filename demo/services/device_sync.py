##############################
# demo/services/device_sync.py
##############################

from django.contrib.auth import get_user_model

from demo.models import DemoDeviceMap
from devices.models import Device, DeviceConfig
from energy.ems.models import EMSSignalSource

User = get_user_model()

MASTER_EMAIL = "ruediger.koenen@web.de"
DEMO_EMAIL = "demo@sharegy.de"


def sync_devices():

    source_user = User.objects.get(
        email=MASTER_EMAIL,
    )

    demo_user = User.objects.get(
        email=DEMO_EMAIL,
    )

    source_home = source_user.homes.first()
    demo_home = demo_user.homes.first()

    if not source_home:
        raise RuntimeError("Master home not found")

    if not demo_home:
        raise RuntimeError("Demo home not found")

    created = 0
    updated = 0
    deleted = 0

    #
    # Nur Geräte des Master-Homes
    #
    source_devices = {d.id: d for d in source_home.devices.all()}

    mappings = {
        m.source_device_id: m
        for m in DemoDeviceMap.objects.select_related(
            "source_device",
            "demo_device",
        )
    }

    #
    # DELETE
    #
    for source_device_id, mapping in list(mappings.items()):

        if source_device_id in source_devices:
            continue

        if mapping.demo_device:
            mapping.demo_device.delete()

        mapping.delete()

        deleted += 1

    #
    # CREATE + UPDATE
    #
    for source_device_id, source_device in source_devices.items():

        #
        # CREATE
        #
        if source_device_id not in mappings:

            new_identifier = (
                f"demo_{source_device.identifier}"
                if source_device.identifier
                else f"demo_{source_device.id}"
            )

            demo_device = Device.objects.create(
                home=demo_home,
                identifier=new_identifier,
                mqtt_profile=source_device.mqtt_profile,
                configured=source_device.configured,
                active=source_device.active,
            )

            DemoDeviceMap.objects.create(
                source_device=source_device,
                demo_device=demo_device,
            )

            if hasattr(source_device, "config"):

                cfg = source_device.config

                DeviceConfig.objects.create(
                    device=demo_device,
                    name=f"{cfg.name} (Demo)",
                    role=cfg.role,
                    measurement_type=cfg.measurement_type,
                    home=demo_home,
                    floor=cfg.floor,
                    room=cfg.room,
                )

            for src in source_device.ems_signal_sources.all():

                EMSSignalSource.objects.create(
                    home=demo_home,
                    device=demo_device,
                    signal_type=src.signal_type,
                )

            created += 1
            continue

        #
        # UPDATE
        #
        mapping = mappings[source_device_id]

        demo_device = mapping.demo_device

        demo_device.mqtt_profile = source_device.mqtt_profile
        demo_device.configured = source_device.configured
        demo_device.active = source_device.active

        demo_device.save()

        if hasattr(source_device, "config"):

            cfg = source_device.config

            demo_cfg, _ = DeviceConfig.objects.get_or_create(
                device=demo_device,
                defaults={
                    "name": f"{cfg.name} (Demo)",
                    "role": cfg.role,
                    "measurement_type": cfg.measurement_type,
                    "home": demo_home,
                    "floor": cfg.floor,
                    "room": cfg.room,
                },
            )

            demo_cfg.name = f"{cfg.name} (Demo)"
            demo_cfg.role = cfg.role
            demo_cfg.measurement_type = cfg.measurement_type
            demo_cfg.floor = cfg.floor
            demo_cfg.room = cfg.room

            demo_cfg.save()

        EMSSignalSource.objects.filter(
            device=demo_device,
        ).delete()

        for src in source_device.ems_signal_sources.all():

            EMSSignalSource.objects.create(
                home=demo_home,
                device=demo_device,
                signal_type=src.signal_type,
            )

        updated += 1

    return {
        "created": created,
        "updated": updated,
        "deleted": deleted,
    }
