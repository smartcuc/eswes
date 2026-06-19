#################
# devices/urls.py
#################

from django.urls import path
from .views import device_list, device_update

urlpatterns = [
    path("", device_list),
    path("<uuid:device_id>/", device_update),
]
