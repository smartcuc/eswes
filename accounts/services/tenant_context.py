#####################################
# accounts/services/tenant_context.py
#####################################

from rest_framework.exceptions import PermissionDenied, ValidationError
from accounts.models import TenantMembership

TENANT_HEADER = "X-Tenant-ID"


def resolve_membershipship(request):
    """
    Liefert die aktive TenantMembership eines Users.

    Regeln:
    1) X-Tenant-ID Header → explizit
    2) Fallback: genau 1 Membership
    """

    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        raise PermissionDenied("Nicht authentifiziert.")

    tenant_id = request.headers.get(TENANT_HEADER)

    qs = TenantMembership.objects.select_related("tenant").filter(
        user=user,
        is_active=True,
    )

    if tenant_id:
        membership = qs.filter(tenant_id=tenant_id).first()
        if not membership:
            raise PermissionDenied("Kein Zugriff auf diesen Tenant.")
        return membership

    count = qs.count()

    if count == 1:
        return qs.first()

    if count == 0:
        raise PermissionDenied("User ist keinem Tenant zugeordnet.")

    raise ValidationError({TENANT_HEADER: "Pflicht bei mehreren Tenants."})
