# optional default
import os
from django.core.exceptions import ImproperlyConfigured

env = os.getenv("DJANGO_SETTINGS_MODULE")

if not env:
    raise ImproperlyConfigured("DJANGO_SETTINGS_MODULE not set")
