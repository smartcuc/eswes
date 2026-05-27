#################
# backend/asgi.py
#################

"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

##application = get_asgi_application()


import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import integrations.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(integrations.routing.websocket_urlpatterns)
        ),
    }
)
