###################
# producer/admin.py
###################

from django.contrib import admin

from producer.models import (
    GeneratorSystem,
    GeneratorString,
)


class GeneratorStringInline(admin.TabularInline):

    model = GeneratorString

    extra = 1

    fields = (
        "name",
        "module_count",
        "peak_power_kwp",
        "orientation",
        "tilt_deg",
        "shading_percent",
    )


@admin.register(GeneratorSystem)
class GeneratorSystemAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "home",
        "system_type",
        "peak_power_kw",
        "string_count",
        "active",
    )

    list_filter = (
        "system_type",
        "active",
    )

    search_fields = (
        "name",
        "home__name",
    )

    inlines = [
        GeneratorStringInline,
    ]
