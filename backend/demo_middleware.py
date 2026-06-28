############################
# backend/demo_middleware.py
############################

from django.http import JsonResponse

class ReadOnlyDemoMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ✅ Demo aktiv, wenn URL /demo enthält
        is_demo = request.headers.get("X-DEMO") == "1"

        if is_demo and request.method in ["POST", "PATCH", "PUT", "DELETE"]:
            return JsonResponse(
                {"error": "read-only demo"},
                status=403
            )

        return self.get_response(request)
    