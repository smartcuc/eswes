#####################
# core/permissions.py
#####################

from rest_framework.permissions import BasePermission
from core.tenant import resolve_scope


class HasTenantContext(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        ctx = resolve_scope(request)

        request.scope = ctx["scope"]
        request.member = ctx["membership"]
        request.tenant = ctx["tenant"]

        return True
    