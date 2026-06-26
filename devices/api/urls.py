#####################
# devices/api/urls.py
#####################


from django.urls import path
from .views import (
    device_setup_options,
    device_list,
    unconfigured_devices,
    latest_device_values,
    configure_device,
    device_timeseries,
    sankey_data,
)

urlpatterns = [
    path("", device_list),
    path("setup-options/", device_setup_options),
    path("unconfigured/", unconfigured_devices),
    path("latest/", latest_device_values),
    path("<int:device_id>/", configure_device),
    path("<int:device_id>/timeseries/", device_timeseries),
    path("sankey/", sankey_data),
]

