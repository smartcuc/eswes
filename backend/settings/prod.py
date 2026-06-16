################################
# backend/settings/prod.py
# Settings for Production-System
################################

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "sharegy.cloud",
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CORS_ALLOWED_ORIGINS = [
    "https://sharegy.cloud",
]

CSRF_TRUSTED_ORIGINS = [
    "https://sharegy.cloud",
]
TRACKING_BASE_URL = "https://api.sharegy.de"