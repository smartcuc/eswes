#####################
# backend/urls.py
#####################
import logging

logger = logging.getLogger(__name__)

"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.routers import DefaultRouter

from metering.api import MeterViewSet, IntervalReadingViewSet, AggregatedReadingViewSet
from .views import api_test, trigger_task
from billing.api.views import consumption_view

router = DefaultRouter()
router.register(r"meters", MeterViewSet, basename="meter")
router.register(r"readings", IntervalReadingViewSet, basename="reading")
router.register(r"aggregates", AggregatedReadingViewSet, basename="aggregate")


def home(request):
    return render(request, "home.html")

    #   path("api/test/", api_test),
    #   path("api/trigger-task/", trigger_task),


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/dashboard/", include("metering.urls_dashboard")),
    path("api/forecast/", include("forecast.urls")),
    path("api/public/", include("forecast.urls_public")),
    path("api/", include("integrations.urls")),
    path("api/", include(router.urls)),
    path("public/billing/", include("billing.api.urls_public")),
    path("api/v1/", include("integrations.api_urls")),
    path("api/consumption/", consumption_view),
]
