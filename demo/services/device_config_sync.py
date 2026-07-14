#####################################
# demo/services/device_config_sync.py
#####################################

from demo.models import DemoDeviceMap


def sync_device_configs():

    for mapping in DemoDeviceMap.objects.all():

        source = mapping.source_device
        demo = mapping.demo_device

        demo.identifier = source.identifier
        demo.active = source.active
        demo.configured = source.configured

        demo.save()

    return True
