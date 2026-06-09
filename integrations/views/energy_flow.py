###################################
# integrations/views/energy_flow.py
###################################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from integrations.services.energy_flow_service import EnergyFlowService


class EnergyFlowView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, tenant_slug):
        data = EnergyFlowService.get_energy_flow(tenant_slug)
        return Response(data)