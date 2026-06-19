##################
# tracking/urls.py
##################

from django.urls import path
from .views import (
    track_magic_click,
    track_email_open,
    track_email_click,
)

urlpatterns = [
    path("magic/<uuid:token>/", track_magic_click),
    path("email/open/<uuid:token>/", track_email_open),
    path("email/click/<uuid:token>/", track_email_click),
]
