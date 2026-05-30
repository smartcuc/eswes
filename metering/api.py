#################
# metering/api.py
#################

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


from core.permissions import HasTenantContext
from core.filter_backends import TenantFilterBackend
from core.permissions_roles import RolePermission


from metering.models import Meter, IntervalReading, AggregatedReading
from metering.serializers import (
    MeterSerializer,
    IntervalReadingSerializer,
    AggregatedReadingSerializer,
)


class TenantScopedMixin:
    """
    Standard:
    - User muss eingeloggt sein
    - Tenant wird erkannt (request.tenant)
    - Daten werden automatisch gefiltert
    - Rollen werden geprüft
    """

    permission_classes = [
        IsAuthenticated,
        HasTenantContext,
        RolePermission,
    ]
    filter_backends = [TenantFilterBackend]


class MeterViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer

    def perform_create(self, serializer):
        # ✅ Tenant wird serverseitig gesetzt (Sicherheits-Layer)
        serializer.save(tenant=self.request.tenant)

    def perform_update(self, serializer):
        serializer.save(tenant=self.request.tenant)


class IntervalReadingViewSet(TenantScopedMixin, viewsets.ReadOnlyModelViewSet):
    queryset = IntervalReading.objects.all()
    serializer_class = IntervalReadingSerializer


class AggregatedReadingViewSet(TenantScopedMixin, viewsets.ReadOnlyModelViewSet):
    queryset = AggregatedReading.objects.all()
    serializer_class = AggregatedReadingSerializer
