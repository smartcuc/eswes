#########################################
# integrations/serializers/energy_flow.py
#########################################

from rest_framework import serializers


class EnergyFlowSerializer(serializers.Serializer):
    nodes = serializers.ListField()
    flows = serializers.ListField()