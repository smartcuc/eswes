#####################
# backend/views.py
#####################
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render
from django.http import JsonResponse
from backend.tasks import process_data


def api_test(request):
    return JsonResponse({"message": "API funktioniert ✅"})


def home(request):
    return render(request, "home.html")


"// test deploy"


def trigger_task(request):
    process_data.delay({"value": 123})
    return JsonResponse({"status": "triggered"})
