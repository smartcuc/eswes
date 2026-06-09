#################
# metering/api.py
#################

from core.viewsets import TenantScopedViewSetMixin

from metering.models import Meter, IntervalReading, AggregatedReading
from metering.serializers import (
    MeterSerializer,
    IntervalReadingSerializer,
    AggregatedReadingSerializer,
)


class MeterViewSet(TenantScopedViewSetMixin):
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer


class IntervalReadingViewSet(TenantScopedViewSetMixin):
    queryset = IntervalReading.objects.all()
    serializer_class = IntervalReadingSerializer


class AggregatedReadingViewSet(TenantScopedViewSetMixin):
    queryset = AggregatedReading.objects.all()
    serializer_class = AggregatedReadingSerializer
    