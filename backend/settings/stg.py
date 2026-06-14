#############################
# backend/settings/stg.py
# Settings for Staging-System
#############################

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "stg.sharegy.cloud",
    "api.stg.sharegy.cloud",
]

# ✅ HTTPS aktiv
HTTPS = True
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"


# ✅ wichtig: echte Domain
FRONTEND_URL = "https://stg.sharegy.cloud"

CORS_ALLOWED_ORIGINS = [
    "https://stg.sharegy.cloud",
]

CSRF_TRUSTED_ORIGINS = [
    "https://stg.sharegy.cloud",
]


# ✅ NICHT im Staging
CORS_ALLOW_ALL_ORIGINS = False

