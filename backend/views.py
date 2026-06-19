#####################
# backend/views.py
#####################
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render
from django.http import JsonResponse
from backend.tasks import process_data
from django_celery_results.models import TaskResult


def api_test(request):
    return JsonResponse({"message": "API funktioniert ✅"})


def home(request):
    return render(request, "home.html")


"// test deploy"


def trigger_task(request):
    process_data.delay({"value": 123})
    return JsonResponse({"status": "triggered"})

def task_view(request):
    # Zeigt die letzten 20 Tasks an
    tasks = TaskResult.objects.all().order_by('-date_done')[:20] 
    return render(request, 'tasks.html', {'tasks': tasks})




