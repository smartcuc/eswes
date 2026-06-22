#################
# devices/urls.py
#################

from django.urls import path
from .views import device_list, device_update, device_metrics
from .views import mqtt_status
from .views import device_status_list
#from devices.views import dashboard

urlpatterns = [
    path("", device_list),
    path("status/", device_status_list),
    path("mqtt-status/", mqtt_status),
    path("by-id/<int:device_id>/", device_update),
    path("by-id/<int:device_id>/metrics/", device_metrics),

]

