##################
# devices/views.py
##################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import os

from .models import Device, DeviceMetric
from .models import Home
from .serializers import DeviceSerializer, DeviceCreateSerializer, DeviceStatusSerializer


# ✅ Geräte Liste + Create (EIN Endpoint!)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def device_list(request):
  
    home = request.user.homes.first()   # ✅ nur lesen, NICHT entscheiden
    
    if not home:
        return Response({"detail": "No home"}, status=400)
    # 🔹 CREATE
    if request.method == "POST":

        serializer = DeviceCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        device = serializer.save()

        return Response({
            "id": device.id,
            "identifier": device.identifier,
            "mqtt_token": device.home.mqtt_token,
            "mqtt_username": device.home.mqtt_username,
            "mqtt_password": device.home.mqtt_password,
            "mqtt_host": os.getenv("MQTT_HOST"),
            "mqtt_port": int(os.getenv("MQTT_PORT")),
        }, status=201)

    # 🔹 LIST
    devices = Device.objects.filter(home=home)

    return Response(
        DeviceSerializer(devices, many=True).data
    )



# ✅ Gerät konfigurieren
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def device_update(request, device_id):

    try:
        device = Device.objects.get(id=device_id, home__in=request.user.homes.all())
    except Device.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DeviceSerializer(device, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    device = serializer.save()

    # ✅ automatisch als konfiguriert markieren
    if not device.configured:
        device.configured = True
        device.save(update_fields=["configured"])

    return Response(DeviceSerializer(device).data)


# ✅ Device Metrics
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_metrics(request, device_id):

    try:
        device = Device.objects.get(id=device_id, home__in=request.user.homes.all())
    except Device.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    metrics = DeviceMetric.objects.filter(device=device).order_by("-timestamp")[:100]

    data = [
        {
            "timestamp": m.timestamp,
            "metric": m.metric,
            "value": m.value,
        }
        for m in metrics
    ]

    return Response(data)


# ✅ REBUILD MQQT PASSWD
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mqtt_status(request):
    homes = Home.objects.all()

    return Response([
        {
            "user": h.user.id,
            "username": h.mqtt_username,
            "provisioned": h.mqtt_provisioned
        }
        for h in homes
    
    ])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_status_list(request):
    print("USER:", request.user)                                                    #
    print("USER HOMES:", list(request.user.homes.all().values("id", "name")))       #
    print("DEVICES:", list(Device.objects.values("id", "identifier", "home_id")))   #

    devices = Device.objects.filter(
        home__in=request.user.homes.all()
    ).select_related("home")

    serializer = DeviceStatusSerializer(devices, many=True)

    return Response(serializer.data)

