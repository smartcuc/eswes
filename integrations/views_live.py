############################
# integrations/views_live.py
############################

from rest_framework.decorators import api_view
from rest_framework.response import Response

from integrations.live_state import LIVE_STATE


@api_view(["GET"])
def live_power(request):

    return Response({"data": LIVE_STATE})
