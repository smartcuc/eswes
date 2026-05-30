###########################
# core/permissions_roles.py
###########################


from rest_framework.permissions import BasePermission, SAFE_METHODS


class RolePermission(BasePermission):
    """
    Role-based Permission für Tenant-Kontext.

    viewer  → nur GET
    manager → GET + POST + PUT
    admin   → alles
    """

    def has_permission(self, request, view):
        member = getattr(request, "member", None)

        if not member:
            return False

        role = member.role

        # ✅ BONUS: Admin Override (HIER!)
        if role == "admin":
            return True

        # ✅ READ erlaubt für viewer/manager
        if request.method in SAFE_METHODS:
            return role in ["viewer", "manager"]

        # ✅ WRITE für manager (admin ist schon oben erlaubt)
        if request.method in ["POST", "PUT", "PATCH"]:
            return role == "manager"

        # ✅ DELETE bleibt für alle außer admin verboten
        if request.method == "DELETE":
            return False

        return False
