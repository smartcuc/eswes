########################
# devices/serializers.py
########################

from rest_framework import serializers
from .models import Device


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
        