########################
# devices/serializers.py
########################

from rest_framework import serializers
from .models import Device
from .models import Home

from devices.tasks import provision_home


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
        

class DeviceCreateSerializer(serializers.ModelSerializer):

    identifier = serializers.CharField()

    class Meta:
        model = Device
        fields = ["identifier"]

    def create(self, validated_data):
        user = self.context["request"].user

        # ✅ Home garantiert setzen
        home = user.homes.first()
        created = False

        # ✅ HIER erzeugen, NICHT in validate()
        if not home:
            home = Home.objects.create(
                user=user,
                name="Mein Zuhause"
            )
            created = True

        device = Device.objects.create(
            identifier=validated_data["identifier"],
            name=validated_data["identifier"],
            home=home
        )

        # ✅ Celery triggern (BESTE STELLE)
        if created:
            provision_home.delay(home.id)

        return device