##################
# core/viewsets.py
##################

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.permissions import HasTenantContext
from core.permissions_roles import RolePermission
from core.filter_backends import TenantFilterBackend


class TenantScopedViewSetMixin(viewsets.ModelViewSet):

    permission_classes = [
        IsAuthenticated,
        HasTenantContext,
        RolePermission,
    ]
    filter_backends = [TenantFilterBackend]


    def get_queryset(self):
        qs = super().get_queryset()

        # ✅ Community Scope
        if self.request.scope == "community":
            if hasattr(qs.model, "tenant"):
                qs = qs.filter(tenant=self.request.tenant)

            if hasattr(qs.model, "owner_membership"):
                qs = qs.filter(owner_membership=self.request.member)

        # ✅ Personal Scope
        else:
            if hasattr(qs.model, "owner_user"):
                qs = qs.filter(owner_user=self.request.user)

            if hasattr(qs.model, "tenant"):
                qs = qs.filter(tenant__isnull=True)

        return qs


    def perform_create(self, serializer):
        data = {}

        if self.request.scope == "community":
            if hasattr(serializer.Meta.model, "tenant"):
                data["tenant"] = self.request.tenant

            if hasattr(serializer.Meta.model, "owner_membership"):
                data["owner_membership"] = self.request.member
        else:
            if hasattr(serializer.Meta.model, "owner_user"):
                data["owner_user"] = self.request.user

            if hasattr(serializer.Meta.model, "tenant"):
                data["tenant"] = None

        serializer.save(**data)


    def perform_update(self, serializer):
        data = {}

        if self.request.scope == "community":
            if hasattr(serializer.Meta.model, "tenant"):
                data["tenant"] = self.request.tenant

            if hasattr(serializer.Meta.model, "owner_membership"):
                data["owner_membership"] = self.request.member
        else:
            if hasattr(serializer.Meta.model, "owner_user"):
                data["owner_user"] = self.request.user

            if hasattr(serializer.Meta.model, "tenant"):
                data["tenant"] = None

        serializer.save(**data)