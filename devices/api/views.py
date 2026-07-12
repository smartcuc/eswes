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

from devices.models import (
    Device,
    DeviceConfig,
    DeviceRole,
    Room,
    Floor,
    Home,
    MQTTProfile,
)

from devices.models import MetricDefinition
from devices.models import DeviceMetric, DeviceMetric1m, DeviceMetric5m
from devices.services.metrics import get_latest_powers

from .serializers import (
    DeviceSerializer,
    DeviceConfigSerializer,
    HomeSerializer,
    DeviceRoleSerializer,
    MQTTProfileSerializer,
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
        "roles": DeviceRoleSerializer(
            roles,
            many=True,
        ).data,

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

    user = request.user

    device = get_object_or_404(Device, id=device_id, home__user=user)

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
    serializer.save()

    # ✅ ✅ ✅ HIER IST DER FIX
    config.refresh_from_db()
    device.configured = config.is_classified()
    device.save(update_fields=["configured"])

    return Response({
        "status": "ok",
        "device": DeviceSerializer(device).data
    })


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

    devices = list(
        Device.objects.filter(
            home__user=request.user,
            active=True,
            pending_delete=False,
        ).select_related("config")
    )

    powers = get_latest_powers([d.id for d in devices])

    metric_map = {m.key: m for m in MetricDefinition.objects.all()}

    result = []

    for d in devices:

        value = powers.get(d.id)

        if value is None:
            continue

        config = getattr(d, "config", None)

        metric_key = (
            config.measurement_type if config and config.measurement_type else "value"
        )

        metric = metric_map.get(metric_key)

        result.append(
            {
                "device": d.id,
                "value": value,
                "unit": metric.unit if metric else "",
            }
        )

    return Response(result)

# ============================================================
# ✅ DEVICE DASHBOARD VALUES
# ============================================================

from datetime import timedelta
from django.utils import timezone
from django.db.models import OuterRef, Subquery
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_dashboard_values(request):
    # 1. Geräte holen
    devices = list(
        Device.objects.filter(
            home__user=request.user,
            active=True,
            pending_delete=False,
        ).select_related("config")
    )

    if not devices:
        return Response([])

    device_ids = [d.id for d in devices]

    # 2. 🔥 OPTIMIERUNG 1: Neueste Metrik pro Gerät OHNE teures distinct()
    # Wir holen uns über eine Subquery exakt die ID des neuesten Eintrags pro Gerät
    newest_metric_id = DeviceMetric.objects.filter(
        device_id=OuterRef('device_id')
    ).order_by('-timestamp').values('id')[:1]

    # Jetzt filtern wir blitzschnell nur über diese IDs
    latest_metrics = DeviceMetric.objects.filter(
        id__in=Subquery(newest_metric_id),
        device_id__in=device_ids
    ).values("device_id", "value", "metric_key")

    latest_map = {m["device_id"]: m for m in latest_metrics}

    # 3. Metrik-Definitionen im Speicher cachen
    metric_map = {m.key: m for m in MetricDefinition.objects.all()}

    # 4. 🔥 OPTIMIERUNG 2: Sparkline-Zeitfenster korrigieren (Code sagt 1h, Kommentar sagt 4h)
    # Wenn du 4h willst, ändere timedelta(hours=1) auf (hours=4)
    # 4. Sparkline-Zeitfenster (1 Stunde für schnellen Last-Check)
    sparkline_since = timezone.now() - timedelta(hours=1)

    # ✅ JETZT KORREKT: Saubere Django-Abfrage ohne den Syntaxfehler
    sparkline_rows = (
        DeviceMetric1m.objects.filter(
            device_id__in=device_ids,
            bucket__gte=sparkline_since,
        )
        .values("device_id", "avg")
        .order_by("device_id", "bucket")  # Nutzt die standardmäßige Sortierung
    )

    # 5. Sparkline-Mapping hocheffizient aufbauen
    sparkline_map = {}
    for row in sparkline_rows:
        d_id = row["device_id"]
        val = row["avg"]

        if d_id not in sparkline_map:
            sparkline_map[d_id] = []

        # Direkt runden – spart Rechenzeit gegenüber float(or 0)
        sparkline_map[d_id].append(round(val, 2) if val is not None else 0.0)

    # 6. Response bauen
    result = []
    for d in devices:
        metric_data = latest_map.get(d.id)
        if not metric_data:
            continue

        config = getattr(d, "config", None)
        metric_key = (
            config.measurement_type
            if config and config.measurement_type
            else metric_data["metric_key"]
        )

        metric = metric_map.get(metric_key)

        result.append({
            "device": d.id,
            "value": metric_data["value"],
            "unit": metric.unit if metric else "",
            "sparkline": sparkline_map.get(d.id, []),
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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mqtt_profile_list(request):

    profiles = MQTTProfile.objects.filter(
        active=True
    ).order_by("name")

    return Response(
        MQTTProfileSerializer(
            profiles,
            many=True,
        ).data
    )
