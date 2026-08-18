#####################
# operations/admin.py
#####################

from django.contrib import admin

from .models import HealthState


@admin.register(HealthState)
class HealthStateAdmin(admin.ModelAdmin):

    list_display = (
        "key",
        "status",
        "value",
        "checked_at",
    )

    list_filter = ("status",)

    search_fields = ("key",)

    readonly_fields = (
        "key",
        "status",
        "value",
        "details",
        "checked_at",
    )

    ordering = (
        "status",
        "key",
    )
