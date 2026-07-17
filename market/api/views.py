#####################
# market/api/views.py
#####################

from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response

from market.services import get_current_spot_price


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_spot_price(request):

    home = request.user.homes.first()

    timezone_name = home.timezone if home and home.timezone else "Europe/Berlin"

    data = get_current_spot_price(timezone_name)

    if not data:
        return Response(
            {"detail": "no price found"},
            status=404,
        )

    return Response(data)
