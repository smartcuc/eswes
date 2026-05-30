##################
# core/viewsets.py
# ################


from rest_framework.permissions import IsAuthenticated
from core.permissions import HasTenantContext
from core.permissions_roles import RolePermission
from core.filter_backends import TenantFilterBackend


class TenantScopedViewSetMixin:
    permission_classes = [
        IsAuthenticated,
        HasTenantContext,
        RolePermission,  # 🔥 NEU
    ]
    filter_backends = [TenantFilterBackend]
