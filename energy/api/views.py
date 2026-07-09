#####################
# energy/api/views.py
#####################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from energy.services.energy import get_energy_data
from energy.services.charts import (get_chart_data,)
from energy.ems.models import EMSSignalSource

from devices.models import Device


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_me(request):
    data = get_energy_data(request.user)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chart_data(request):

    metric = request.GET.get("metric")
    period = request.GET.get(
        "period",
        "24h",
    )
    
    if period not in [
        "1h",
        "6h",
        "24h",
        "5d",
    ]:
        return Response(
            {"detail": "invalid period"},
            status=400,
        )

    if metric not in [
        "load",
        "pv",
        "grid",
        "today",
    ]:
        return Response(
            {"detail": "invalid metric"},
            status=400,
        )

    if metric == "pv":

        device_ids = list(
            EMSSignalSource.objects.filter(
                home__user=request.user,
                signal_type="pv",
            ).values_list(
                "device_id",
                flat=True,
            )
        )

    else:

        device_ids = list(
            EMSSignalSource.objects.filter(
                home__user=request.user,
                signal_type="grid",
            ).values_list(
                "device_id",
                flat=True,
            )
        )

    data = get_chart_data(
        device_ids,
        period,
    )

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

