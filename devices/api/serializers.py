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

        room = data.get("room") or getattr(self.instance, "room", None)
        floor = data.get("floor") or getattr(self.instance, "floor", None)
        home = data.get("home") or getattr(self.instance, "home", None)

        # ✅ 1. Room → Floor ableiten
        if room and not floor:
            if room.floor:
                floor = room.floor
                data["floor"] = floor
            else:
                raise serializers.ValidationError("Room hat keine Etage")

        # ✅ 2. Floor → Home ableiten (wenn kein home gesetzt)
        if not home and floor:
            if not floor.home:
                raise serializers.ValidationError("Etage hat kein Zuhause")
            home = floor.home

        # ✅ 3. Fallback: User hat genau 1 Home
        if not home and user:
            homes = user.homes.all()
            if homes.count() == 1:
                home = homes.first()

        # 🚨 FINAL: Muss IMMER gesetzt sein
        if not home:
            raise serializers.ValidationError("Kein gültiges Zuhause ableitbar")

        data["home"] = home


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