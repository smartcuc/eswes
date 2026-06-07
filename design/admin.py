#################
# design/admin.py
#################

from django.contrib import admin
from .models import TenantTheme


@admin.register(TenantTheme)
class TenantThemeAdmin(admin.ModelAdmin):
    list_display = ("tenant", "primary", "secondary", "button")
