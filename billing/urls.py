from django.urls import path
from billing.api.views import consumption_view

urlpatterns = [
    path("api/consumption/", consumption_view),
]
