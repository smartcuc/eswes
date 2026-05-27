#
#
#


from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsSameTenant


class ReadingView(APIView):
    permission_classes = [IsAuthenticated, IsSameTenant]
