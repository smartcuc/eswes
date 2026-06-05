############################
# fforecast/services_bias.py
############################

from forecast.services_forecast_accuracy import calculate_forecast_accuracy


def calculate_bias(tenant, start_date, end_date):

    result = calculate_forecast_accuracy(tenant, start_date, end_date)

    if result.get("status") != "ok":
        return {"status": "error", "reason": "no-accuracy-data"}

    return {
        "status": "ok",
        "temp_bias": result["mean_temp_error"],
        "cloud_bias": result["mean_cloud_error"],
        "radiation_bias": result["mean_radiation_error"],
        "points": result["points_compared"],
    }


def apply_bias(forecast_row, bias):

    if bias.get("status") != "ok":
        return forecast_row

    # 🔥 einfache Korrektur
    forecast_row.temperature_c = (
        forecast_row.temperature_c - bias["temp_bias"]
        if forecast_row.temperature_c is not None
        else None
    )

    forecast_row.cloud_cover_pct = (
        forecast_row.cloud_cover_pct - bias["cloud_bias"]
        if forecast_row.cloud_cover_pct is not None
        else None
    )

    forecast_row.shortwave_radiation_wm2 = (
        forecast_row.shortwave_radiation_wm2 - bias["radiation_bias"]
        if forecast_row.shortwave_radiation_wm2 is not None
        else None
    )

    return forecast_row
