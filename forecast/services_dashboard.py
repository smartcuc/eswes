################################
# forecast/services_dashboard.py
################################


from forecast.models import SolarForecast
from collections import defaultdict


def forecast_tenant_from_db(tenant):
    result = defaultdict(float)

    qs = SolarForecast.objects.filter(tenant=tenant)

    for row in qs:
        result[row.timestamp] += float(row.forecast_kw)

    return [
        {
            "timestamp": ts,
            "forecast_kw": round(val, 3),
        }
        for ts, val in sorted(result.items())
    ]
