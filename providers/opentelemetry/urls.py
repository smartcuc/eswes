#################################
# providers/opentelemetry/urls.py
#################################

from django.urls import path

from .views import otlp_metrics

urlpatterns = [
    path("v1/metrics", otlp_metrics),
]
