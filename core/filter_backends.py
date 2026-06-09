#########################
# core/filter_backends.py
#########################

from rest_framework.filters import BaseFilterBackend

class TenantFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "member", None)

        if not tenant or not membership:
            return queryset.none()

        # ✅ Tenant Isolation
        if hasattr(queryset.model, "tenant"):
            queryset = queryset.filter(tenant=tenant)

        # ✅ Membership Isolation (wichtig!)
        if hasattr(queryset.model, "owner_membership"):
            queryset = queryset.filter(owner_membership=membership)

        return queryset