#####################
# core/permissions.py
#####################

from rest_framework.permissions import BasePermission
from core.tenant import resolve_member


class HasTenantContext(BasePermission):
    """
    Setzt request.member und request.tenant.
    Läuft vor dem View-Code.
    """

    def has_permission(self, request, view):
        member = resolve_member(request)
        request.member = member
        request.tenant = member.tenant
        return True
