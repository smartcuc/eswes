################
# core/tenant.py
################

from rest_framework.exceptions import ValidationError
from accounts.models import TenantMembership

TENANT_HEADER = "X-Tenant-ID"


def resolve_scope(request):
    user = request.user
    tenant_id = request.headers.get(TENANT_HEADER)

    # ✅ COMMUNITY MODE
    if tenant_id:
        membership = TenantMembership.objects.select_related("tenant").filter(
            user=user,
            tenant_id=tenant_id,
            is_active=True,
        ).first()

        if not membership:
            raise ValidationError({TENANT_HEADER: "Invalid tenant"})

        return {
            "scope": "community",
            "membership": membership,
            "tenant": membership.tenant,
        }

    # ✅ PERSONAL MODE
    return {
        "scope": "personal",
        "membership": None,
        "tenant": None,
    }
