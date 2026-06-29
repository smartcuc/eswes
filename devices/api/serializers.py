############################
# devices/api/serializers.py
############################

from rest_framework import serializers
from devices.models import Device, DeviceConfig, DeviceRole, Room, Floor, Home


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

    # READ
    role = DeviceRoleSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    floor = FloorSerializer(read_only=True)

    # WRITE
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=DeviceRole.objects.all(),
        source="role",
        write_only=True,
        allow_null=True,
        required=False
    )

    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        source="room",
        write_only=True,
        allow_null=True,
        required=False
    )

    floor_id = serializers.PrimaryKeyRelatedField(
        queryset=Floor.objects.all(),
        source="floor",
        write_only=True,
        allow_null=True,
        required=False
    )

    home_id = serializers.PrimaryKeyRelatedField(
        queryset=Home.objects.all(),
        source="home",
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = DeviceConfig
        fields = (
            "name",
            "measurement_type",
            "role",
            "role_id",
            "room",
            "room_id",
            "floor",
            "floor_id",
            "home_id",
        )

    # ✅ ✅ ✅ HIER IST DER FIX

    def validate(self, data):

        request = self.context.get("request")
        user = request.user if request else None

        home = data.get("home") or getattr(self.instance, "home", None)

        # ✅ DEFAULT HOME setzen
        if not home and user:
            home = user.homes.first()

        # 🚨 FINAL: Muss IMMER gesetzt sein
        if not home:
            raise serializers.ValidationError("Kein Zuhause verfügbar")

        data["home"] = home

        return data


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