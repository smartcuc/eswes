#########################################
# accounts/permissions.py
#########################################

from functools import wraps
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from accounts.models import TenantMembership
from core.models import Tenant


# ✅ Rollen → Rechte Mapping
ROLE_PERMISSIONS = {
    "admin": [
        "manage_members",
        "manage_invites",
        "edit_data",
        "view_data",
    ],
    "editor": [
        "edit_data",
        "view_data",
    ],
    "viewer": [
        "view_data",
    ],
}


# ✅ zentrale Permission Funktion
def has_permission(user, tenant, permission):
    membership = TenantMembership.objects.filter(
        user=user,
        tenant=tenant,
        is_active=True
    ).first()

    if not membership:
        return False

    role = membership.role

    return permission in ROLE_PERMISSIONS.get(role, [])


# ✅ einfacher Zugriff (ohne spezielle Permission)
def has_tenant_access(user, tenant):
    return TenantMembership.objects.filter(
        user=user,
        tenant=tenant,
        is_active=True
    ).exists()


# ✅ DRF Permission: gleicher Tenant Zugriff
class IsSameTenant(BasePermission):

    def has_object_permission(self, request, view, obj):
        return has_tenant_access(request.user, obj.tenant)


# ✅ DRF Permission: darf Objekt bearbeiten
class CanEditTenantObject(BasePermission):

    def has_object_permission(self, request, view, obj):
        return has_permission(request.user, obj.tenant, "edit_data")


# ✅ DECORATOR für Views (sehr stark)
def require_permission(permission):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):

            tenant_id = request.data.get("tenant_id")
            
            if not tenant_id:
                return Response(
                    {"error": "tenant_id missing"},
                    status=400
                )

            try:
                tenant = Tenant.objects.get(id=tenant_id)
            except Tenant.DoesNotExist:
                return Response(
                    {"error": "tenant not found"},
                    status=404
                )

            # ✅ Check Permission
            if not has_permission(request.user, tenant, permission):
                return Response(
                    {"error": "not allowed"},
                    status=403
                )

            # ✅ Tenant an Request hängen
            request.tenant = tenant

            return view_func(self, request, *args, **kwargs)

        return wrapper
    return decorator

