#####################
# devices/api/urls.py
#####################


from django.urls import path

from .views import user_preference

urlpatterns = [
    path("<str:key>/", user_preference),
]

