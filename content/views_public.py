#########################
# content/views_public.py
#########################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import TenantPage
from .serializers import TenantPageSerializer


class PublicTenantPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, tenant_slug, page_slug):

        page = get_object_or_404(
            TenantPage, tenant__slug=tenant_slug, slug=page_slug, is_public=True
        )

        serializer = TenantPageSerializer(page)

        tenant = page.tenant  # ✅ sauber, da page schon Tenant kennt

        theme = getattr(tenant, "theme", None)

        return Response(
            {
                **serializer.data,
                "theme": {
                    "primary": getattr(theme, "primary", None),
                    "secondary": getattr(theme, "secondary", None),
                    "button": getattr(theme, "button", None),
                },
            }
        )
