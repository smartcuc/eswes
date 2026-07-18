#
#
#

from django.contrib import admin

from producer.models import (
    GeneratorSystem,
    GeneratorString,
)


class GeneratorStringInline(admin.TabularInline):
    model = GeneratorString
    extra = 1


@admin.register(GeneratorSystem)
class GeneratorSystemAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "home",
        "system_type",
        "peak_power_kw",
        "active",
    )

    list_filter = (
        "system_type",
        "active",
    )

    inlines = [
        GeneratorStringInline,
    ]
