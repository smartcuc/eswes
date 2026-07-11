#####################
# energy/api/views.py
#####################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from zoneinfo import ZoneInfo
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from devices.models import Device

from energy.services.energy import get_energy_data
from energy.services.charts import (get_chart_data,)
from energy.ems.models import EMSSignalSource

from openpyxl import Workbook
from openpyxl.styles import Font

import csv


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

    home = request.user.homes.first()
    timezone_name = home.timezone if home else "UTC"

    data = get_chart_data(
        device_ids,
        period,
        timezone_name=timezone_name,
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

# ----------------
# Export - Excel
# ----------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_chart_xlsx(request):

    metric = request.GET.get("metric")
    period = request.GET.get("period", "24h")

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

    home = request.user.homes.first()
    timezone_name = home.timezone if home else "UTC"

    export_time = (
        timezone.now().astimezone(ZoneInfo(timezone_name)).strftime("%d.%m.%Y %H:%M")
    )

    data = get_chart_data(
        device_ids,
        period,
        timezone_name=timezone_name,
    )

    wb = Workbook()
    ws = wb.active

    ws.title = f"{metric}_{period}"

    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 18

    ws["A1"].font = Font(
        bold=True,
        size=16,
    )

    metric_labels = {
        "load": "Bedarf",
        "pv": "Erzeugung",
        "grid": "Bezug/Einspeisung",
        "today": "Tagesverbrauch",
    }

    ws["A8"].font = Font(bold=True)
    ws["B8"].font = Font(bold=True)

    ws["A1"] = "Sharegy Energieexport"

    ws["A3"] = "Metrik"
    ws["B3"] = metric_labels.get(
        metric,
        metric,
    )

    ws["A4"] = "Zeitraum"
    ws["B4"] = period

    ws["A5"] = "Einheit"
    ws["B5"] = data["unit"]

    ws["A6"] = "Exportiert"
    ws["B6"] = export_time

    # Leerzeile
    ws.append([])

    ws["A8"] = "Zeitpunkt"
    ws["B8"] = f"Wert ({data['unit']})"

    row = 9

    for ts, value in zip(
        data["export_timestamps"],
        data["values"],
    ):
        ws.cell(row=row, column=1, value=ts)
        ws.cell(row=row, column=2, value=value)
        row += 1

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    )

    metric_label = metric_labels.get(
        metric,
        metric,
    )

    safe_label = metric_label.replace("/", "-").replace("\\", "-").replace(" ", "_")

    response["Content-Disposition"] = f'attachment; filename="sharegy_{safe_label}_{period}.xlsx"'

    wb.save(response)

    return response


# ----------------
# Export - CSV
# ----------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_chart_csv(request):

    metric = request.GET.get("metric")
    period = request.GET.get("period", "24h")

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

    home = request.user.homes.first()
    timezone_name = home.timezone if home else "UTC"

    export_time = (
        timezone.now().astimezone(ZoneInfo(timezone_name)).strftime("%d.%m.%Y %H:%M")
    )

    data = get_chart_data(
        device_ids,
        period,
        timezone_name=timezone_name,
    )

    metric_labels = {
        "load": "Bedarf",
        "pv": "Erzeugung",
        "grid": "Bezug/Einspeisung",
        "today": "Tagesverbrauch",
    }

    response = HttpResponse(
        content_type="text/csv"
    )

    metric_label = metric_labels.get(
        metric,
        metric,
    )

    safe_label = metric_label.replace("/", "-").replace("\\", "-").replace(" ", "_")

    response["Content-Disposition"] = (
        f'attachment; filename="sharegy_{safe_label}_{period}.csv"'
    )

    writer = csv.writer(
        response,
        delimiter=";"
    )

    writer.writerow(["Sharegy Energieexport"])
    writer.writerow([])

    writer.writerow(["Metrik", metric_labels.get(metric, metric)])
    writer.writerow(["Zeitraum", period])
    writer.writerow(["Einheit", data["unit"]])
    writer.writerow(["Exportiert", export_time])

    writer.writerow([])

    writer.writerow([
        "Zeitpunkt",
        f"Wert ({data['unit']})"
    ])

    for ts, value in zip(
        data["export_timestamps"],
        data["values"],
    ):
        writer.writerow(
            [
                ts,
                str(value).replace(".", ","),
            ]
        )

    return response
