######################
# devices/api/views.py
######################

from django.db.models import Avg

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from devices.models import DeviceType, Room
from devices.models import Device, DeviceMetric
from .serializers import DeviceTypeSerializer, RoomSerializer
from .serializers import DeviceConfigureSerializer
from .serializers import DeviceListSerializer, DeviceDetailSerializer

from collections import defaultdict

from devices.models import (
    Device,
    DeviceType,
    MetricDefinition,
    DeviceSelectedMetric,  # ✅ DAS FEHLT DIR
    Room
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_setup_options(request):

    user = request.user

    # 👉 nur eigene Homes → Rooms
    rooms = Room.objects.filter(floor__home__user=user)

    types = DeviceType.objects.all()

    return Response({
        "types": DeviceTypeSerializer(types, many=True).data,
        "rooms": RoomSerializer(rooms, many=True).data
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def configure_device(request, device_id):

    user = request.user

    try:
        device = Device.objects.get(id=device_id, home__user=user)
    except Device.DoesNotExist:
        return Response({"error": "Device not found"}, status=404)

    serializer = DeviceConfigureSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data

    device_type = DeviceType.objects.get(id=data["type_id"])
    room = Room.objects.get(id=data["room_id"])

    # ✅ Device setzen
    device.type = device_type
    device.role = device_type.role  # 🔥 automatisch!
    device.room = room
    device.configured = True
    device.save()

    # ✅ alte Metrics löschen
    device.selected_metrics.all().delete()

    # ✅ neue Metrics setzen
    for key in data["metric_keys"]:
        metric = MetricDefinition.objects.get(key=key)

        DeviceSelectedMetric.objects.create(
            device=device,
            metric=metric
        )

    return Response({"status": "configured"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_list(request):

    devices = Device.objects.filter(home__user=request.user)

    return Response(
        DeviceListSerializer(devices, many=True).data
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_detail(request, device_id):

    try:
        device = Device.objects.get(
            id=device_id,
            home__user=request.user
        )
    except Device.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    return Response(DeviceDetailSerializer(device).data)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sankey_data(request):

    from django.db.models import OuterRef, Subquery
    from devices.models import Device, DeviceMetric

    user = request.user  # ✅ FIX 1

    # ✅ Subquery für latest power
    latest_metrics = DeviceMetric.objects.filter(
        device=OuterRef("pk"),
        metric_key="power"
    ).order_by("-timestamp")

    devices = Device.objects.filter(
        home__user=user,
        configured=True
    ).select_related("type", "role").annotate(
        latest_power=Subquery(latest_metrics.values("value")[:1])
    )

    producers, consumers, storages = [], [], []

    for d in devices:
        power = d.latest_power or 0

        if not d.role or not d.type:
            continue

        if d.role.key == "producer":
            producers.append((d, power))
        elif d.role.key == "consumer":
            consumers.append((d, power))
        elif d.role.key == "both":
            storages.append((d, power))

    # =====================================================
    # ✅ BUILD GRAPH
    # =====================================================
    nodes, links = [], []
    node_ids = set()

    def nid(d):
        return f"{d.type.key}_{d.id}"

    def add_node(i, label):
        if i not in node_ids:
            nodes.append({"id": i, "label": label})
            node_ids.add(i)

    def add_link(s, t, v):
        if v and v > 0:
            links.append({
                "source": s,
                "target": t,
                "value": round(v, 2)
            })

    # ✅ Nodes
    for d in devices:  # ✅ FIX 2
        add_node(nid(d), d.name)

    HOUSE = "house"
    add_node(HOUSE, "Haus")

    # ✅ Production Sum
    total_production = sum(p for _, p in producers if p and p > 0)

    # ✅ Producer → House
    for d, p in producers:
        add_link(nid(d), HOUSE, p)

    # ✅ Storage Logic
    for d, p in storages:

        if p > 0:
            # entlädt
            add_link(nid(d), HOUSE, p)

        elif p < 0:
            # lädt
            charge = abs(p)

            for prod, pp in producers:
                if total_production > 0 and pp > 0:
                    share = pp / total_production
                    add_link(nid(prod), nid(d), charge * share)

    # ✅ House → Consumer
    for d, p in consumers:
        add_link(HOUSE, nid(d), p)

    return Response({
        "nodes": nodes,
        "links": links
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sankey_timeseries(request):

    user = request.user
    start = request.GET.get("from")
    end = request.GET.get("to")

    from devices.models import Device, DeviceMetric
    from django.db.models import Avg

    devices = Device.objects.filter(
        home__user=user,
        configured=True
    ).select_related("type", "role")

    producers, consumers, storages = [], [], []

    for d in devices:
        if not d.role:
            continue

        avg_power = DeviceMetric.objects.filter(
            device=d,
            metric_key="power",
            timestamp__range=[start, end]
        ).aggregate(avg=Avg("value"))["avg"] or 0

        if d.role.key == "producer":
            producers.append((d, avg_power))
        elif d.role.key == "consumer":
            consumers.append((d, avg_power))
        elif d.role.key == "both":
            storages.append((d, avg_power))

    hours = 1  # TODO: berechnen aus start/end

    def energy(power):
        return power * hours  # kWh approx

    nodes, links = [], []
    node_ids = set()

    def nid(d): return f"{d.type.key}_{d.id}"

    def add_node(i, label):
        if i not in node_ids:
            nodes.append({"id": i, "label": label})
            node_ids.add(i)

    def add_link(s, t, v):
        if v > 0:
            links.append({"source": s, "target": t, "value": round(v, 2)})

    for d in devices:
        add_node(nid(d), d.name)

    HOUSE = "house"
    add_node(HOUSE, "Haus")

    total_prod = sum(energy(p) for _, p in producers if p)

    for d, p in producers:
        add_link(nid(d), HOUSE, energy(p))

    for d, p in storages:
        if p > 0:
            add_link(nid(d), HOUSE, energy(p))
        elif p < 0:
            charge = abs(energy(p))

            for prod, pp in producers:
                if total_prod > 0:
                    share = energy(pp) / total_prod
                    add_link(nid(prod), nid(d), charge * share)

    for d, p in consumers:
        add_link(HOUSE, nid(d), energy(p))

    return Response({
        "nodes": nodes,
        "links": links
    })
