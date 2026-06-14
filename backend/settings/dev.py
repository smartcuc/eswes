#########################
# backend/settings/dev.py
# Settings for Dev-System
#########################

from .base import *

DEBUG.1", "localhost"]DEBUG = True

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
]

