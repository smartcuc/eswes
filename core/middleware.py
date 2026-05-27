########################
# core/middleware.py
########################
import logging

logger = logging.getLogger(__name__)

import uuid
from .logging_context import request_id_var

import uuid
from .logging_context import request_id_var


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rid = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        token = request_id_var.set(rid)

        try:
            response = self.get_response(request)
            response["X-Request-Id"] = rid
            return response
        finally:
            request_id_var.reset(token)
