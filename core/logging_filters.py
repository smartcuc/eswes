#########################
# core/logging_filters.py
#########################
import logging

logger = logging.getLogger(__name__)

from .logging_context import request_id_var, tenant_id_var, event_id_var


class ContextFilter:
    def filter(self, record):
        record.request_id = request_id_var.get() or "-"
        record.tenant_id = tenant_id_var.get() or "-"
        record.event_id = event_id_var.get() or "-"
        return True
