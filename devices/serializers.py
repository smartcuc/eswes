########################
# devices/serializers.py
########################

from rest_framework import serializers
from .models import Device, Home

from devices.tasks import provision_home
from devices.services.device_health import device_status


# ✅ READ SERIALIZER (für Dashboard etc.)
class DeviceSerializer(serializers.ModelSerializer):

    config = serializers.SerializerMethodField()

    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = [
            "id",
            "identifier",
            "display_name",
            "configured",
            "config",
        ]

    def get_display_name(self, obj):
        if hasattr(obj, "config") and obj.config:
            return obj.config.display_name()
        return obj.identifier

    def get_config(self, obj):
        if hasattr(obj, "config") and obj.config:
            return {
                "name": obj.config.name,
                "measurement_type": obj.config.measurement_type,
                "role": obj.config.role.id if obj.config.role else None,
                "floor": obj.config.floor.id if obj.config.floor else None,
                "room": obj.config.room.id if obj.config.room else None,
            }
        return None


# ✅ CREATE SERIALIZER (für POST /api/devices/)
class DeviceCreateSerializer(serializers.ModelSerializer):

    identifier = serializers.CharField()
    name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Device
        fields = ["identifier", "name"]

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

        identifier = validated_data["identifier"]
        name = validated_data.get("name")

        device, _ = Device.objects.get_or_create(
            home=home,
            identifier=identifier
        )

        # ✅ Name gehört in DeviceConfig
        if name:
            from devices.models import DeviceConfig

            config, _ = DeviceConfig.objects.get_or_create(
                device=device,
                defaults={"home": home}
            )

            config.name = name
            config.save()

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
    