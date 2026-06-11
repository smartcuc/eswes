##############################################
# core/api/serializers_dashboard_timeseries.py
##############################################

from rest_framework import serializers


class DashboardTimeseriesPointSerializer(serializers.Serializer):
    period_start = serializers.DateTimeField()
    consumption_kwh = serializers.DecimalField(max_digits=18, decimal_places=3)
    generation_kwh = serializers.DecimalField(max_digits=18, decimal_places=3)
    self_consumption_kwh = serializers.DecimalField(max_digits=18, decimal_places=3)
    grid_import_kwh = serializers.DecimalField(max_digits=18, decimal_places=3)
    grid_export_kwh = serializers.DecimalField(max_digits=18, decimal_places=3)


class DashboardTimeseriesResponseSerializer(serializers.Serializer):
    from_ts = serializers.DateTimeField(source="from")
    to_ts = serializers.DateTimeField(source="to")
    step = serializers.CharField()
    rows = serializers.IntegerField()
    series = DashboardTimeseriesPointSerializer(many=True)
