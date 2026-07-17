####################
# market/api/urls.py
####################

from django.urls import path
from .views import current_spot_price

urlpatterns = [
    path(
        "current/",
        current_spot_price,
        name="current-spot-price",
    ),
]
