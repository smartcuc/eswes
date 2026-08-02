##################################
# providers/opentelemetry/views.py
##################################
import logging

from django.utils import timezone
from datetime import UTC, datetime

from rest_framework.decorators import (
    api_view,
    permission_classes,
)

from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from devices.models import (
    Device,
    DeviceMetric,
    DeviceConfig,
    DeviceResource,
    Home,
    MetricDefinition,
)

from .parser import get_attr

logger = logging.getLogger("django")


@api_view(["POST"])
@permission_classes([AllowAny])
def otlp_metrics(request):

    created = 0

    resource_metrics = request.data.get("resourceMetrics", [])

    for resource_metric in resource_metrics:

        resource = resource_metric.get("resource", {})

        attributes = resource.get("attributes", [])
        resource_attributes = {}

        for attr in attributes:

            key = attr.get("key")

            value = get_attr(
                [attr],
                key,
            )

            if key and value is not None:
                resource_attributes[key] = value

        resource_attributes.pop(
            "home.token",
            None,
        )

        device_id = get_attr(
            attributes,
            "device.id",
        )

        token = get_attr(
            attributes,
            "home.token",
        )

        if not device_id:
            continue

        if not token:
            continue

        try:
            home = Home.objects.get(mqtt_token=token)

        except Home.DoesNotExist:

            logger.warning(
                "otlp.invalid_token",
                extra={
                    "token": token,
                    "device": device_id,
                },
            )

            continue

        device, _ = Device.objects.get_or_create(
            home=home,
            identifier=device_id,
        )

        resource_obj, _ = DeviceResource.objects.get_or_create(
            device=device,
        )

        if resource_obj.attributes != resource_attributes:
            resource_obj.attributes = resource_attributes
            resource_obj.save(update_fields=["attributes"])

        config, _ = DeviceConfig.objects.get_or_create(
            device=device,
            defaults={
                "home": home,
                "name": device.identifier,
            },
        )

        for scope_metric in resource_metric.get("scopeMetrics", []):

            for metric in scope_metric.get("metrics", []):

                metric_name = metric.get("name")

                metric_definition = MetricDefinition.objects.filter(
                    key=metric_name,
                ).first()

                if not metric_definition:

                    logger.warning(
                        "otlp.unsupported_metric",
                        extra={
                            "metric": metric_name,
                            "device": device_id,
                        },
                    )

                    continue

                if not config.metric_definition:

                    logger.info(
                        "otlp.metric_definition_assigned",
                        extra={
                            "device": device_id,
                            "metric": metric_name,
                        },
                    )

                    config.metric_definition = metric_definition
                    config.save(
                        update_fields=[
                            "metric_definition",
                        ]
                    )

                gauge = metric.get("gauge")

                if not gauge:
                    continue

                for point in gauge.get("dataPoints", []):

                    value = point.get("asDouble")

                    if value is None:
                        value = point.get("asInt")

                    if value is None:
                        continue

                    ns = point.get("timeUnixNano")

                    if ns is not None:
                        timestamp = datetime.fromtimestamp(
                            int(ns) / 1_000_000_000,
                            tz=UTC,
                        )
                    else:
                        timestamp = timezone.now()

                    DeviceMetric.objects.create(
                        device=device,
                        metric_key="value",
                        value=float(value),
                        unit="",
                        data={
                            "otel_metric": metric_name,
                        },
                        timestamp=timestamp,
                    )

                    created += 1

    return Response(
        {
            "status": "ok",
            "created": created,
        }
    )
