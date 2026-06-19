########################
# devices/serializers.py
########################

from rest_framework import serializers
from .models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            "id",
            "identifier",
            "name",
            "role",
            "home",
            "floor",
            "room",
            "configured",
        ]
        read_only_fields = ["identifier"]