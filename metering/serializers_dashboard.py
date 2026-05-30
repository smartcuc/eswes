###################################
# metering/serializers_dashboard.py
###################################

from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    period_start_from = serializers.DateTimeField(allow_null=True)
    period_start_to = serializers.DateTimeField(allow_null=True)

    consumption_kwh = serializers.DecimalField(max_digits=18, decimal_places=3)
    generation_kwh = serializers.DecimalField(max_digits=18, decimal_places=3)
    self_consumption_kwh = serializers.DecimalField(max_digits=18, decimal_places=3)
    grid_import_kwh = serializers.DecimalField(max_digits=18, decimal_places=3)
    grid_export_kwh = serializers.DecimalField(max_digits=18, decimal_places=3)

    rows = serializers.IntegerField()
