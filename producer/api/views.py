########################
# producer/api/views.py
########################

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from producer.models import GeneratorSystem, GeneratorString, GeneratorType,  Orientation


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generator_list(request):

    home = request.user.homes.first()

    if not home:
        return Response([])

    systems = (
        GeneratorSystem.objects.filter(
            home=home,
            active=True,
        )
        .prefetch_related("strings", "generator_type")
        .order_by("name")
    )

    data = []

    for system in systems:

        strings = []

        for string in system.strings.all():

            strings.append(
                {
                    "id": str(string.id),
                    "name": string.name,
                    "module_count": string.module_count,
                    "peak_power_kwp": float(string.peak_power_kwp),
                    "orientation": string.orientation.name,
                    "orientation_id": string.orientation.id,
                    "tilt_deg": string.tilt_deg,
                    "shading_percent": float(string.shading_percent),
                }
            )

        data.append(
            {
                "id": str(system.id),
                "device_id": (
                        system.device.id
                        if system.device
                        else None
                    ),
                "name": system.name,
                "type": system.generator_type.key,
                "type_label": system.generator_type.name,
                "peak_power_kw": float(system.peak_power_kw),
                "inverter_power_kw": (
                    float(system.inverter_power_kw)
                    if system.inverter_power_kw
                    else None
                ),
                "battery_capacity_kwh": (
                    float(system.battery_capacity_kwh)
                    if system.battery_capacity_kwh
                    else None
                ),
                "string_count": system.string_count,
                "total_string_power_kwp": system.total_string_power_kwp,
                "strings": strings,
            }
        )

    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generator_create(request):

    home = request.user.homes.first()

    if not home:
        return Response(
            {"detail": "Kein Home gefunden."},
            status=400,
        )
    
    generator_type = GeneratorType.objects.get(
        id=request.data["generator_type"]
    )

    system = GeneratorSystem.objects.create(
        home=home,
        generator_type=generator_type,
        name=request.data.get("name"),
        system_type=request.data.get("system_type"),
        peak_power_kw=request.data.get("peak_power_kw"),
        inverter_power_kw=request.data.get("inverter_power_kw"),
        battery_capacity_kwh=request.data.get("battery_capacity_kwh"),
    )

    return Response(
        {
            "id": str(system.id),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def string_create(request):

    generator = GeneratorSystem.objects.get(id=request.data["generator_id"])
    orientation = Orientation.objects.get(id=request.data["orientation_id"]
    )

    string = GeneratorString.objects.create(
        generator=generator,
        name=request.data["name"],
        module_count=request.data["module_count"],
        peak_power_kwp=request.data["peak_power_kwp"],
        orientation=orientation,
        tilt_deg=request.data["tilt_deg"],
        shading_percent=request.data.get(
            "shading_percent",
            0,
        ),
    )

    return Response(
        {
            "id": str(string.id),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generator_type_list(request):

    data = []

    for item in GeneratorType.objects.filter(
        active=True,
    ):

        data.append(
            {
                "id": item.id,
                "key": item.key,
                "name": item.name,
            }
        )

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def orientation_list(request):

    data = []

    for item in Orientation.objects.filter(
        active=True,
    ):

        data.append(
            {
                "id": item.id,
                "key": item.key,
                "name": item.name,
                "azimuth_deg": item.azimuth_deg,
            }
        )

    return Response(data)

