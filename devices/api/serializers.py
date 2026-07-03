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

    
    display_name = serializers.CharField(
            source="name",
            required=False,
            allow_blank=True,
        )


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
            "display_name",
            "measurement_type",
            "energy_source",
            "energy_group",
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

        # ✅ FIELD EXISTENZ prüfen (WICHTIG)
        if "home" in data:
            home = data["home"]

            # ❌ explizit null → NICHT erlauben
            if home is None:
                # stattdessen aktuelles behalten
                home = getattr(self.instance, "home", None)
        else:
            # nicht gesendet → aktuelles behalten
            home = getattr(self.instance, "home", None)

        # ✅ fallback: user default
        if not home and user:
            home = user.homes.first()

        # 🚨 FINAL GUARANTEE
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

    last_seen = serializers.DateTimeField(
        read_only=True,
        allow_null=True,
    )

    delete_after = serializers.DateTimeField(
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Device
        
        fields = (
            "id",
            "identifier",
            "display_name",
            "classified",
            "last_seen",
            "delete_after",
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
    

# ============================================================
# ✅ DEVICE
# ============================================================

class HomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Home
        fields = ("id", "name")