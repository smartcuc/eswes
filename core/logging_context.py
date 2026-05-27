#########################
# core/logging_context.py
#########################

import contextvars

request_id_var = contextvars.ContextVar("request_id", default=None)
tenant_id_var = contextvars.ContextVar("tenant_id", default=None)
event_id_var = contextvars.ContextVar("event_id", default=None)
