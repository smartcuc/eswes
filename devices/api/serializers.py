############################
# devices/api/serializers.py
############################

from rest_framework import serializers
from devices.models import Device
#, DeviceSelectedMetric

from devices.models import (
    Device,
    MetricDefinition,
#    DeviceSelectedMetric,
    Room
)


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricDefinition
        fields = ("key", "name", "unit")


""" class DeviceTypeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.key")
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = DeviceType
        fields = ("id", "key", "name", "role", "metrics")

    def get_metrics(self, obj):
        mappings = DeviceTypeMetric.objects.filter(device_type=obj)
        metrics = [m.metric for m in mappings]
        return MetricSerializer(metrics, many=True).data
     """

class RoomSerializer(serializers.ModelSerializer):
    floor = serializers.CharField(source="floor.name")
    home = serializers.CharField(source="floor.home.name")

    class Meta:
        model = Room
        fields = ("id", "name", "floor", "home")


class DeviceConfigureSerializer(serializers.Serializer):
    type_id = serializers.IntegerField()
    metric_keys = serializers.ListField(
        child=serializers.CharField()
    )
    room_id = serializers.IntegerField()
""" 
    def validate(self, data):
        try:
            device_type = DeviceType.objects.get(id=data["type_id"])
        except DeviceType.DoesNotExist:
            raise serializers.ValidationError("Invalid device type")

        # ✅ erlaubte Metrics holen
        allowed_metrics = set(
            device_type.allowed_metrics.values_list("metric__key", flat=True)
        )

        for key in data["metric_keys"]:
            if key not in allowed_metrics:
                raise serializers.ValidationError(
                    f"Metric '{key}' not allowed for this device type"
                )

        return data

 """
class DeviceListSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    role = serializers.CharField(source="role.key", default=None)
    room = serializers.CharField(source="room.name", default=None)
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = (
            "id",
            "name",
            "identifier",
            "configured",
            "type",
            "role",
            "room",
            "metrics",
        )

    def get_type(self, obj):
        if not obj.type:
            return None
        return {
            "key": obj.type.key,
            "name": obj.type.name
        }

    def get_metrics(self, obj):
        return list(
            obj.selected_metrics.values_list("metric__key", flat=True)
        )
    

class DeviceDetailSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    role = serializers.CharField(source="role.key", default=None)
    room = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = "__all__"

    def get_type(self, obj):
        if not obj.type:
            return None
        return {
            "key": obj.type.key,
            "name": obj.type.name
        }

    def get_room(self, obj):
        if not obj.room:
            return None

        return {
            "id": obj.room.id,
            "name": obj.room.name,
            "floor": obj.room.floor.name
        }

    def get_metrics(self, obj):
        metrics = DeviceSelectedMetric.objects.filter(device=obj)

        return [
            {
                "key": m.metric.key,
                "name": m.metric.name,
                "unit": m.metric.unit
            }
            for m in metrics
        ]


