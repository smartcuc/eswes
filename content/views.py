##################
# content/views.py
##################

from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import TenantPage
from .serializers import TenantPageSerializer


class TenantPageViewSet(ReadOnlyModelViewSet):
    serializer_class = TenantPageSerializer

    def get_queryset(self):
        user = self.request.user

        # 🔥 View-Level Security!
        return TenantPage.objects.filter(
            tenant__memberships__user=user, tenant__memberships__is_active=True
        ).distinct()
