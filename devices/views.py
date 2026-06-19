##################
# devices/views.py
##################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Device
from .serializers import DeviceSerializer


# ✅ Geräte Liste (inkl. neue Geräte erkennen)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_list(request):
    devices = Device.objects.filter(user=request.user).order_by("-created_at")
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data)


# ✅ Gerät konfigurieren
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def device_update(request, device_id):
    try:
        device = Device.objects.get(id=device_id, user=request.user)
    except Device.DoesNotExist:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DeviceSerializer(device, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    device = serializer.save()

    # ✅ Wenn User konfiguriert → setzt configured=True
    if not device.configured:
        device.configured = True
        device.save(update_fields=["configured"])

    return Response(DeviceSerializer(device).data)