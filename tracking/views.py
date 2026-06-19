###################
# tracking/views.py
###################

from django.http import HttpResponse
from django.shortcuts import redirect
from .services import track_event


def track_magic_click(request, token):
    track_event(
        name="magic_link_click",
        metadata={"token": str(token)},
        request=request,
    )
    return redirect(f"/magic-login/{token}")


def track_email_open(request, token):
    track_event(
        name="email_open",
        metadata={"token": str(token)},
        request=request,
    )

    pixel = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!'
        b'\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
        b'\x4c\x01\x00;'
    )

    return HttpResponse(pixel, content_type="image/gif")


def track_email_click(request, token):
    track_event(
        name="email_click",
        metadata={"token": str(token)},
        request=request,
    )
    return redirect(f"/magic-login/{token}")
