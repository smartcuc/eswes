#####################
# devices/api/urls.py
#####################


from django.urls import path
from .views import (
    device_setup_options,
    device_list,
    unconfigured_devices,
    configure_device,
    sankey_data,
)

urlpatterns = [
    path("", device_list),
    path("setup-options/", device_setup_options),
    path("unconfigured/", unconfigured_devices),
    path("<int:device_id>/", configure_device),
    path("sankey/", sankey_data),
]

