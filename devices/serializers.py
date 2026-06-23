########################
# devices/serializers.py
########################

from rest_framework import serializers
from .models import Device, Home, DeviceMetric

from devices.tasks import provision_home
from devices.services.device_health import device_status


# ✅ READ SERIALIZER (für Dashboard etc.)
class DeviceSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="role.label", read_only=True)
    floor_display = serializers.CharField(source="floor.name", read_only=True)
    room_display = serializers.CharField(source="room.name", read_only=True)

    class Meta:
        model = Device
        fields = [
            "id",
            "identifier",
            "name",
            "role",
            "role_display",
            "home",
            "floor",
            "floor_display",
            "room",
            "room_display",
            "configured",
        ]
        read_only_fields = ["identifier"]


# ✅ CREATE SERIALIZER (für POST /api/devices/)
class DeviceCreateSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField()

    class Meta:
        model = Device
        fields = ["identifier"]

    def create(self, validated_data):
        user = self.context["request"].user

        # ✅ Home holen oder erstellen
        home = user.homes.first()
        created = False

        if not home:
            home = Home.objects.create(
                user=user,
                name="Mein Zuhause"
            )
            created = True

        # ✅ Device erstellen oder holen
        device, _ = Device.objects.get_or_create(
            home=home,
            identifier=validated_data["identifier"],
            defaults={"name": validated_data["identifier"]},
        )

        # ✅ Provisioning nur bei neuem Home
        if created:
            provision_home.delay(home.id)

        return device


# ✅ STATUS SERIALIZER (für Monitoring)
class DeviceStatusSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    last_seen = serializers.DateTimeField(allow_null=True)

    class Meta:
        model = Device
        fields = [
            "id",
            "identifier",
            "name",
            "status",
            "last_seen",
        ]

    def get_status(self, obj):
        return device_status(obj)
    