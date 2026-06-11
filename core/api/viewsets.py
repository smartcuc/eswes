#
#
#

from rest_framework import viewsets
from core.models import Meter, IntervalReading, AggregatedReading, BalanceSlot
from core.api.serializers import (
    MeterSerializer,
    IntervalReadingSerializer,
    AggregatedReadingSerializer,
    BalanceSlotSerializer,
)
from core.viewsets import TenantScopedViewSetMixin


class MeterViewSet(TenantScopedViewSetMixin):
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer


class IntervalReadingViewSet(TenantScopedViewSetMixin):
    queryset = IntervalReading.objects.all()
    serializer_class = IntervalReadingSerializer


class AggregatedReadingViewSet(TenantScopedViewSetMixin):
    queryset = AggregatedReading.objects.all()
    serializer_class = AggregatedReadingSerializer


class BalanceSlotViewSet(TenantScopedViewSetMixin):
    queryset = BalanceSlot.objects.all()
    serializer_class = BalanceSlotSerializer
