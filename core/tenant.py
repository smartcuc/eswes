################
# core/tenant.py
################


from rest_framework.exceptions import PermissionDenied, ValidationError
from metering.models import Member

TENANT_HEADER = "X-Tenant-ID"


def resolve_membership(request):
    """
    Tenant automatisch erkennen:
    1) X-Tenant-ID Header
    2) Fallback: wenn User genau 1 Membership hat
    """

    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        raise PermissionDenied("Nicht authentifiziert.")

    tenant_id = request.headers.get(TENANT_HEADER)

    if tenant_id:
        member = (
            Member.objects.select_related("tenant")
            .filter(user=user, tenant_id=tenant_id)
            .first()
        )

        if not member:
            raise PermissionDenied("Kein Zugriff auf diesen Tenant.")
        return member

    # Fallback: genau 1 Tenant
    qs = Member.objects.select_related("tenant").filter(user=user)
    count = qs.count()

    if count == 1:
        return qs.first()

    if count == 0:
        raise PermissionDenied("User ist keinem Tenant zugeordnet.")

    # mehrere Tenants → Header Pflicht
    raise ValidationError({TENANT_HEADER: "Pflicht, wenn User mehrere Tenants hat."})
