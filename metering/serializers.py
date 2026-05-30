#########################
# metering/serializers.py
#########################


from rest_framework import serializers
from metering.models import Meter, IntervalReading, AggregatedReading


class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = "__all__"
        read_only_fields = ["tenant"]  # tenant wird serverseitig gesetzt


class IntervalReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntervalReading
        fields = "__all__"


class AggregatedReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregatedReading
        fields = "__all__"
