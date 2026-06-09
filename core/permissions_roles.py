###########################
# core/permissions_roles.py
###########################

from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    REQUIRED_ROLES = {
        "POST": ["admin", "owner"],
        "PUT": ["admin", "owner"],
        "PATCH": ["admin", "owner"],
        "DELETE": ["owner"],
    }

    def has_permission(self, request, view):
        membership = getattr(request, "member", None)

        if not membership:
            return False

        allowed_roles = self.REQUIRED_ROLES.get(request.method)

        if not allowed_roles:
            return True  # GET/SAFE

        return membership.role in allowed_roles