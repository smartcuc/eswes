######################
# accounts/api/urls.py
######################

from django.urls import path
from .views import UserSettingsView, UpdateOnboardingStepView
from .views import UserProfileView
from .views import UserUsageModeView
from .views import UserLanguageView
from .views import UseInviteView
from .views import CreateInviteView
from .views import MyTenantView
from .views import UpdateMemberRoleView
from .views import RemoveMemberView
from .views import DeactivateInviteView
from .views import RequestMagicLinkView, MagicLoginView


urlpatterns = [
    path("settings/", UserSettingsView.as_view()),
    path("onboarding-step/", UpdateOnboardingStepView.as_view()),
]

urlpatterns += [
    path("profile/", UserProfileView.as_view()),
]

urlpatterns += [
    path("usage-mode/", UserUsageModeView.as_view()),
]

urlpatterns += [
    path("language/", UserLanguageView.as_view()),
]

urlpatterns += [
   path("use-invite/", UseInviteView.as_view()),
]

urlpatterns += [
    path("create-invite/", CreateInviteView.as_view()),
]

urlpatterns += [
    path("my-tenant/", MyTenantView.as_view()),
]

urlpatterns += [
path("update-role/", UpdateMemberRoleView.as_view()),
]

urlpatterns += [
path("remove-member/", RemoveMemberView.as_view()),
]

urlpatterns += [
path("deactivate-invite/", DeactivateInviteView.as_view()),
]

urlpatterns += [
    path("request-magic-link/", RequestMagicLinkView.as_view()),
    path("magic-login/", MagicLoginView.as_view()),
]