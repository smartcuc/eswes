#
#
#

from rest_framework.serializers import ModelSerializer
from core.models import Meter, IntervalReading, AggregatedReading, BalanceSlot


class MeterSerializer(ModelSerializer):
    class Meta:
        model = Meter
        fields = "__all__"


class IntervalReadingSerializer(ModelSerializer):
    class Meta:
        model = IntervalReading
        fields = "__all__"


class AggregatedReadingSerializer(ModelSerializer):
    class Meta:
        model = AggregatedReading
        fields = "__all__"


class BalanceSlotSerializer(ModelSerializer):
    class Meta:
        model = BalanceSlot
        fields = "__all__"
        