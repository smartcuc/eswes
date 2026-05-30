##################
# accounts/urls.py
##################


from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import TokenByEmailView, MeView, LogoutView

urlpatterns = [
    path("token/", TokenByEmailView.as_view(), name="token_by_email"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
