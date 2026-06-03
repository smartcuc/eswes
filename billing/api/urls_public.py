###########################
# billing/api/urls_public.py
############################

from django.urls import path
from billing.api.views_public import public_consumption_view

urlpatterns = [
    path("consumption/", public_consumption_view, name="public-consumption"),
]
