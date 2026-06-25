############################
# devices/api/serializers.py
############################

from rest_framework import serializers
from devices.models import Device, DeviceConfig, DeviceRole, Room, Floor


# ============================================================
# ✅ ROLE
# ============================================================

class DeviceRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceRole
        fields = ("id", "key", "label")


# ============================================================
# ✅ LOCATION
# ============================================================

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "name")


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ("id", "name")


# ============================================================
# ✅ CONFIG
# ============================================================

class DeviceConfigSerializer(serializers.ModelSerializer):

    role = DeviceRoleSerializer(read_only=True)

    role_id = serializers.PrimaryKeyRelatedField(
        queryset=DeviceRole.objects.all(),
        source="role",
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = DeviceConfig
        fields = (
            "name",
            "role",
            "role_id",
            "measurement_type",
            "floor",
            "room",
        )


# ============================================================
# ✅ DEVICE
# ============================================================

class DeviceSerializer(serializers.ModelSerializer):

    config = DeviceConfigSerializer(read_only=True)

    display_name = serializers.SerializerMethodField()
    classified = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = (
            "id",
            "identifier",
            "display_name",
            "classified",
            "config",
        )

    def get_display_name(self, obj):
        if hasattr(obj, "config") and obj.config:
            return obj.config.display_name()
        return obj.identifier

    def get_classified(self, obj):
        if hasattr(obj, "config") and obj.config:
            return obj.config.is_classified()
        return False