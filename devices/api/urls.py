#####################
# devices/api/urls.py
#####################

from django.urls import path
from .views import device_setup_options
from .views import configure_device
from .views import device_list, device_detail
from .views import sankey_data, sankey_timeseries


urlpatterns = [
    path("setup-options/", device_setup_options),
    path("<int:device_id>/configure/", configure_device),
    path("", device_list),
    path("<int:device_id>/", device_detail),
    path("sankey/", sankey_data),
    path("sankey/timeseries/", sankey_timeseries),
]
