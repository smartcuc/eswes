#######################
# tracking/analytics.py
#######################

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import EventLog
from .constants import FUNNEL_STEPS

User = get_user_model()


def _unique_users(queryset):
    return queryset.filter(user__isnull=False)\
        .values("user")\
        .distinct()\
        .count()

def get_kpis(tenant=None, context="global"):
    now = timezone.now()

    base_qs = EventLog.objects.filter(context=context)

    if context == "tenant" and tenant:
        base_qs = base_qs.filter(tenant=tenant)

    # Daily Active Users (last 24h)
    dau = _unique_users(
        base_qs.filter(created_at__gte=now - timedelta(days=1))
    )

    # Funnel user counts (deduplicated)
    landing_users = _unique_users(base_qs.filter(name="landing_view"))
    signup_users = _unique_users(base_qs.filter(name="signup_success"))
    login_users = _unique_users(base_qs.filter(name="login"))

    return {
        "dau": dau,
        "conversion_landing_signup": round(
            (signup_users / landing_users * 100) if landing_users else 0, 2
        ),
        "conversion_signup_login": round(
            (login_users / signup_users * 100) if signup_users else 0, 2
        ),
    }


def get_funnel(tenant=None, context="global"):
    steps = []

    for label, event_name in FUNNEL_STEPS:
        qs = EventLog.objects.filter(
            name=event_name,
            context=context
        )

        if context == "tenant" and tenant:
            qs = qs.filter(tenant=tenant)

        count = _unique_users(qs)

        steps.append({
            "label": label,
            "count": count
        })

    return steps
