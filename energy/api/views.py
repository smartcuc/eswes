#####################
# energy/api/views.py
#####################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from devices.models import Device
from energy.services.energy import get_energy_data


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_me(request):
    data = get_energy_data(request.user)
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def configure_device(request, device_id):
    device = get_object_or_404(Device, id=device_id, user=request.user)

    device.role = request.data.get("role")
    device.room = request.data.get("room")
    device.name = request.data.get("name", device.name)

    device.configured = True
    device.save()

    return Response({"status": "ok"})

