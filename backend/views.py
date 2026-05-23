from django.shortcuts import render
from django.http import JsonResponse


def api_test(request):
    return JsonResponse({"message": "API funktioniert ✅"})


def home(request):
    return render(request, "home.html")
"// test deploy" 
