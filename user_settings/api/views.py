######################
# devices/api/views.py
######################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user_settings.models import UserPreference
from .serializers import UserPreferenceSerializer


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def user_preference(request, key):

    preference, _ = UserPreference.objects.get_or_create(
        user=request.user,
        key=key,
    )

    if request.method == "GET":
        serializer = UserPreferenceSerializer(preference)
        return Response(serializer.data)

    serializer = UserPreferenceSerializer(
        preference,
        data=request.data,
        partial=True,
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)

