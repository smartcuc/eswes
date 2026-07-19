########################
# producer/api/views.py
########################

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from producer.models import GeneratorSystem


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
        .prefetch_related("strings")
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

                    "module_count":
                        string.module_count,

                    "peak_power_kwp":
                        float(string.peak_power_kwp),

                    "orientation":
                        string.get_orientation_display(),

                    "tilt_deg":
                        string.tilt_deg,

                    "shading_percent":
                        float(
                            string.shading_percent
                        ),
                }
            )

            data.append(
                {
                    "id": str(system.id),

                    "name": system.name,

                    "type": system.system_type,

                    "peak_power_kw":
                        float(system.peak_power_kw),

                    "inverter_power_kw":
                        (
                            float(system.inverter_power_kw)
                            if system.inverter_power_kw
                            else None
                        ),

                    "battery_capacity_kwh":
                        (
                            float(system.battery_capacity_kwh)
                            if system.battery_capacity_kwh
                            else None
                        ),

                    "string_count":
                        system.string_count,

                    "total_string_power_kwp":
                        system.total_string_power_kwp,

                    "strings":
                        strings,
                }
            )

        return Response(data)

    data.append(
        {
            "id": str(system.id),

            "name": system.name,

            "type": system.system_type,

            "peak_power_kw":
                float(system.peak_power_kw),

            "inverter_power_kw":
                (
                    float(system.inverter_power_kw)
                    if system.inverter_power_kw
                    else None
                ),

            "battery_capacity_kwh":
                (
                    float(system.battery_capacity_kwh)
                    if system.battery_capacity_kwh
                    else None
                ),

            "string_count":
                system.string_count,

            "total_string_power_kwp":
                system.total_string_power_kwp,

            "strings":
                strings,
        }
    )

    return Response(data)
