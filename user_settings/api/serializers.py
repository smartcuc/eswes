############################
# devices/api/serializers.py
############################

from rest_framework import serializers
from ..models import UserPreference

from user_settings.models import UserPreference


class UserPreferenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPreference
        fields = (
            "key",
            "value",
        )
