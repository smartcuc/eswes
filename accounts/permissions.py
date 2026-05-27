#
# accounts/permissions.py
#

from rest_framework.permissions import BasePermission


class IsSameTenant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.tenant_id == request.user.tenant_id
