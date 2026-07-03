######################
# devices/api/views.py
######################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery
from datetime import timedelta
from django.utils import timezone

from devices.models import DeviceMetric, MetricDefinition
from devices.models import Device, DeviceConfig, DeviceRole, Room, Floor, Home

from devices.models import DeviceMetric, DeviceMetric1m, DeviceMetric5m

from .serializers import (
    DeviceSerializer,
    DeviceConfigSerializer,
    HomeSerializer
#    RoomSerializer,
#    FloorSerializer,
)


# ============================================================
# ✅ SETUP OPTIONS
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_setup_options(request):

    roles = DeviceRole.objects.all()
    rooms = Room.objects.all()
    floors = Floor.objects.all()

    # ✅ wenn du measurement types brauchst:
    from devices.models import MetricDefinition
    metrics = MetricDefinition.objects.all()

    return Response({
        "roles": [
            {"id": r.id, "label": r.label}
            for r in roles
        ],
        "rooms": [
            {"id": r.id, "name": r.name}
            for r in rooms
        ],
        "floors": [
            {"id": f.id, "name": f.name}
            for f in floors
        ],
        "measurement_types": [
            {"key": m.key, "name": m.name}
            for m in metrics
        ],
    })


# ============================================================
# ✅ ALL DEVICES
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_list(request):

    devices = Device.objects.filter(
            home__user=request.user,
            active=True,
            pending_delete=False,
        )

    return Response(DeviceSerializer(devices, many=True).data)


# ============================================================
# ✅ UNCONFIGURED (für Modal)
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unconfigured_devices(request):

    devices = Device.objects.filter(
            home__user=request.user,
            active=True,
            pending_delete=False,
        )

    result = []

    for d in devices:
        config = getattr(d, "config", None)

        if not config or not config.is_classified():
            result.append(DeviceSerializer(d).data)

    return Response({"devices": result})


# ============================================================
# ✅ CONFIGURE DEVICE
# ============================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def configure_device(request, device_id):

    print("\n================================")
    print("PATCH CALLED")
    print("DEVICE:", device_id)
    print("DATA:", request.data)
    print("================================\n")

    user = request.user

    device = get_object_or_404(
        Device,
        id=device_id,
        home__user=user
    )

    config, _ = DeviceConfig.objects.get_or_create(
        device=device,
        defaults={"home": device.home}
    )

    serializer = DeviceConfigSerializer(
        config,
        data=request.data,
        partial=True
    )

    serializer.is_valid(raise_exception=True)

    print("\nVALIDATED DATA:")
    print(serializer.validated_data)

    serializer.save()

    config.refresh_from_db()

    print("\nAFTER SAVE:")
    print("name =", config.name)
    print("energy_source =", config.energy_source)
    print("energy_group =", config.energy_group)

    device.configured = config.is_classified()
    device.save(update_fields=["configured"])

    response_data = {
        "status": "ok",
        "device": DeviceSerializer(device).data
    }

    print("\nRESPONSE:")
    print(response_data)
    print("================================\n")

    return Response(response_data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sankey_data(request):

    user = request.user

    latest_metrics = DeviceMetric.objects.filter(
        device=OuterRef("pk"),
        metric_key="power"
    ).order_by("-timestamp")

    devices = (
        Device.objects
        .filter(home__user=user)
        .select_related("config__role")
        .annotate(
            latest_power=Subquery(
                latest_metrics.values("value")[:1]
            )
        )
    )

    nodes = []
    links = []
    added = set()

    def nid(d):
        return f"device_{d.id}"

    def label(d):
        if d.config:
            return d.config.display_name()
        return d.identifier

    def add_node(i, l):
        if i not in added:
            nodes.append({"id": i, "label": l})
            added.add(i)

    def add_link(s, t, v):
        if v and v > 0:
            links.append({
                "source": s,
                "target": t,
                "value": round(v, 2)
            })

    HOUSE = "house"
    add_node(HOUSE, "Haus")

    producers, consumers, storages = [], [], []

    for d in devices:
        config = getattr(d, "config", None)
        if not config or not config.is_classified():
            continue

        role = config.role
        if not role:
            continue

        power = d.latest_power or 0

        if role.key == "producer":
            producers.append((d, power))
        elif role.key == "consumer":
            consumers.append((d, power))
        elif role.key == "both":
            storages.append((d, power))

    for d, _ in producers + consumers + storages:
        add_node(nid(d), label(d))

    total_prod = sum(p for _, p in producers if p > 0)

    for d, p in producers:
        add_link(nid(d), HOUSE, p)

    for d, p in storages:
        if p > 0:
            add_link(nid(d), HOUSE, p)
        elif p < 0:
            charge = abs(p)

            for pd, pp in producers:
                if total_prod > 0 and pp > 0:
                    share = pp / total_prod
                    add_link(nid(pd), nid(d), charge * share)

    for d, p in consumers:
        add_link(HOUSE, nid(d), p)

    return Response({
        "nodes": nodes,
        "links": links
    })


# ============================================================
# ✅ LATEST DEVCE VALUE
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def latest_device_values(request):

    latest_metrics = DeviceMetric.objects.filter(
        device=OuterRef("pk")
    ).order_by("-timestamp")

    devices = (
        Device.objects
        .filter(home__user=request.user)
        .annotate(
            latest_value=Subquery(
                latest_metrics.values("value")[:1]
            ),
            latest_key=Subquery(
                latest_metrics.values("metric_key")[:1]
            ),
        )
    )

    result = []

    for d in devices:

        if not d.latest_key:
            continue

        config = getattr(d, "config", None)

        if config and config.measurement_type:
            metric_key = config.measurement_type
        else:
            metric_key = d.latest_key

        metric = MetricDefinition.objects.filter(
            key=metric_key
        ).first()

        result.append({
            "device": d.id,
            "value": d.latest_value,
            "unit": metric.unit if metric else "",
        })

    return Response(result)


# ============================================================
# ✅ TIMESERIES API
# ============================================================

def get_range_config(range_str):
    if range_str == "1h":
        return {
            "model": DeviceMetric,
            "delta": timedelta(hours=1),
            "field": "timestamp",
            "value_field": "value",
        }

    if range_str == "6h":
        return {
            "model": DeviceMetric1m,
            "delta": timedelta(hours=6),
            "field": "bucket",
            "value_field": "avg",
        }

    if range_str == "24h":
        return {
            "model": DeviceMetric1m,
            "delta": timedelta(hours=24),
            "field": "bucket",
            "value_field": "avg",
        }

    if range_str == "7d":
        return {
            "model": DeviceMetric5m,
            "delta": timedelta(days=7),
            "field": "bucket",
            "value_field": "avg",
        }

    raise ValueError("invalid_range")


@api_view(["GET"])
def device_timeseries(request, device_id):

    range_str = request.GET.get("range", "24h")

    try:
        config = get_range_config(range_str)
    except ValueError:
        return Response({"error": "invalid_range"}, status=400)

    now = timezone.now()

    # Ende immer sauber runden
    field = config["field"]

    if field == "bucket":
        now = now.replace(second=0, microsecond=0)

    start = now - config["delta"]

    qs = (
        config["model"].objects
        .filter(device_id=device_id)
        .filter(**{
            f"{field}__gte": start,
            f"{field}__lte": now,
        })
        .order_by(field)
    )

    points = []

    for row in qs:
        t = getattr(row, field).timestamp()
        v = getattr(row, config["value_field"])

        points.append({
            "t": int(t),
            "v": v,
            "min": getattr(row, "min", None),
            "max": getattr(row, "max", None),
        })

    return Response({
        "device": device_id,
        "range": range_str,
        "points": points,
    })


# ============================================================
# ✅ HOME-LIST
# ============================================================

@api_view(["GET"])
def list_homes(request):
    homes = Home.objects.filter(user=request.user)
    serializer = HomeSerializer(homes, many=True)
    return Response(serializer.data)


# ============================================================
# ✅ REMOVE DEVICES
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_devices(request):

    device_ids = request.data.get("device_ids", [])

    if not device_ids:

        return Response(
            {"detail": "No devices selected"},
            status=400,
        )

    delete_after = timezone.now() + timedelta(days=7)

    updated = Device.objects.filter(
        id__in=device_ids,
        home__user=request.user,
        active=True,
    ).update(
        active=False,
        pending_delete=True,
        delete_after=delete_after,
    )

    return Response({
        "updated": updated,
        "delete_after": delete_after,
    })


# ============================================================
# ✅ RESTORE DEVICES
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def restore_devices(request):

    device_ids = request.data.get("device_ids", [])

    updated = Device.objects.filter(
        id__in=device_ids,
        home__user=request.user,
        pending_delete=True,
    ).update(
        active=True,
        pending_delete=False,
        delete_after=None,
    )

    return Response({
        "updated": updated,
    })


# ============================================================
# ✅ TRASH BIN
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trash_devices(request):

    devices = Device.objects.filter(
        home__user=request.user,
        pending_delete=True,
    )

    return Response(
        DeviceSerializer(devices, many=True).data
    )


# ============================================================
# ✅ PURGE DEVICES
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purge_devices(request):

    device_ids = request.data.get("device_ids", [])

    deleted, _ = Device.objects.filter(
        id__in=device_ids,
        home__user=request.user,
        pending_delete=True,
    ).delete()

    return Response({
        "deleted": deleted,
    })


# ============================================================
# ✅ TRASH COUNT
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trash_count(request):

    count = Device.objects.filter(
        home__user=request.user,
        pending_delete=True,
    ).count()

    return Response({
        "count": count,
    })

