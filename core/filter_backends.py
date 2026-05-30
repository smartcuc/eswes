#########################
# core/filter_backends.py
#########################


from rest_framework.filters import BaseFilterBackend


class TenantFilterBackend(BaseFilterBackend):
    """
    Automatischer Tenant-Filter.
    Wenn das Model ein tenant-Feld hat, wird auf request.tenant gefiltert.
    """

    def filter_queryset(self, request, queryset, view):
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return queryset

        model = queryset.model

        # tenant-Feld vorhanden? dann tenant-scope erzwingen
        if hasattr(model, "tenant") or hasattr(model, "tenant_id"):
            return queryset.filter(tenant=tenant)

        return queryset
