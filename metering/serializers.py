#########################
# metering/serializers.py
#########################

from rest_framework import serializers
from metering.models import Meter, IntervalReading, AggregatedReading


class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = "__all__"

        # 🔒 CRITICAL: niemals vom Client setzen lassen
        read_only_fields = (
            "tenant",
            "owner_membership",
        )


class IntervalReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntervalReading
        fields = "__all__"

        # 🔒 wichtig: diese Felder sind system-controlled
        read_only_fields = (
            "tenant",
            "meter",
        )


class AggregatedReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregatedReading
        fields = "__all__"

        # 🔒 system-generated Daten
        read_only_fields = (
            "tenant",
            "meter",
            "owner_membership",
        )