######################
# tracking/services.py
######################

from .models import EventLog


def get_client_ip(request):
    if not request:
        return None

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def track_event(name, metadata=None, user=None, request=None):
    metadata = metadata or {}

    if not user and request and request.user.is_authenticated:
        user = request.user

    ip = get_client_ip(request)

    return EventLog.objects.create(
        name=name,
        user=user,
        anonymous_id=metadata.get("anonymous_id"),

        context=metadata.get("context", "global"),
        tenant=metadata.get("tenant") if metadata.get("context") == "tenant" else None,

        session_id=metadata.get("session_id"),

        source=metadata.get("source"),
        campaign=metadata.get("campaign"),

        metadata=metadata,
        ip=ip,
    )
