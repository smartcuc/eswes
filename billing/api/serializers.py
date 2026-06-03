# billing/api/serializers.py

from rest_framework import serializers
from billing.models import UserBalanceSlot


class UserBalanceSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBalanceSlot
        fields = [
            "period_start",
            "consumption_kwh",
            "grid_import_kwh",
        ]
