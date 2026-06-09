###################
# accounts/views.py
###################


from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.models import TenantMembership

from .serializers import TokenByEmailSerializer

User = get_user_model()


class TokenByEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenByEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        memberships = TenantMembership.objects.filter(
            user=user,
            is_active=True
        ).select_related("tenant")

        tenants = []
        for m in memberships:
            tenants.append(
                {
                    "tenant_id": str(m.tenant.id),
                    "tenant_name": m.tenant.name,
                    "role": m.role,
                }
            )

        return Response({
            "id": str(user.id),
            "email": user.email,
            "tenants": tenants
        })


class LogoutView(APIView):
    """
    JWT Logout = Refresh Token blacklisten (optional).
    Wenn du Blacklisting willst: simplejwt[blacklist] App aktivieren.
    Fürs erste: Client löscht Tokens lokal.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Minimal: Client löscht Tokens, wir bestätigen nur.
        return Response({"status": "ok"})


