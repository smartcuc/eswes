################################
# backend/settings/prod.py
# Settings for Production-System
################################

from .base import *

DEBUG = False
load_dotenv("/var/www/sharegy/shared/.env")

ALLOWED_HOSTS = [
    "sharegy.de",
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CORS_ALLOWED_ORIGINS = [
    "https://sharegy.de",
]

CSRF_TRUSTED_ORIGINS = [
    "https://sharegy.de",
]
TRACKING_BASE_URL = "https://api.sharegy.de"