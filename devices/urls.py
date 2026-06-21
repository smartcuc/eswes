#################
# devices/urls.py
#################

from django.urls import path
from .views import device_list, device_update, device_metrics
from .views import mqtt_status
#from devices.views import dashboard

urlpatterns = [
    path("", device_list),
    path("mqtt-status/", mqtt_status),
    path("<uuid:device_id>/", device_update),
]


urlpatterns += [
    path("api/devices/<int:device_id>/metrics/", device_metrics),  
]

