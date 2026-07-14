###############
# demo/tasks.py
###############

from celery import shared_task
from demo.services.metric_replication import (
    sync_latest_metrics,
)


@shared_task
def sync_demo_metrics():
    return sync_latest_metrics()
