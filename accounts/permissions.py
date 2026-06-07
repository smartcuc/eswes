#########################
# accounts/permissions.py
#########################

from rest_framework.permissions import BasePermission
from accounts.models import TenantMembership


class IsSameTenant(BasePermission):

    def has_object_permission(self, request, view, obj):
        return TenantMembership.objects.filter(
            user=request.user, tenant_id=obj.tenant_id, is_active=True
        ).exists()


class CanEditTenantObject(BasePermission):

    def has_object_permission(self, request, view, obj):
        return TenantMembership.objects.filter(
            user=request.user,
            tenant_id=obj.tenant_id,
            role__in=["admin", "editor"],
            is_active=True,
        ).exists()


def has_tenant_access(user, tenant_id):
    return TenantMembership.objects.filter(
        user=user, tenant_id=tenant_id, is_active=True
    ).exists()


class IsSameTenant(BasePermission):

    def has_object_permission(self, request, view, obj):
        return has_tenant_access(request.user, obj.tenant_id)
