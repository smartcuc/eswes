###############
# demo/tasks.py
###############

from celery import shared_task

from demo.services.metric_replication import (
    sync_latest_metrics,
)

from demo.services.device_sync import (
    sync_devices,
)

from demo.services.device_config_sync import (
    sync_device_configs,
)

from demo.services.cleanup import (
    cleanup_demo_metrics,
)

@shared_task
def sync_demo_metrics():
    return sync_latest_metrics()


@shared_task
def sync_demo_devices():
    return sync_devices()


@shared_task
def sync_demo_configs():
    return sync_device_configs()


@shared_task
def cleanup_demo():
    return cleanup_demo_metrics()
