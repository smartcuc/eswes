########################
# content/urls_public.py
########################

from django.urls import path
from .views_public import PublicTenantPageView

urlpatterns = [
    path("public/<slug:tenant_slug>/<slug:page_slug>/", PublicTenantPageView.as_view()),
]
