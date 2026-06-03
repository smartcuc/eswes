####################
# accounts/admin.py
####################


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, UserProfile, UserSettings
from django.db import models


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "email", "username", "is_active", "is_verified", "is_staff")
    search_fields = ("email", "username")
    ordering = ("email",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Tibber Integration",
            {
                "fields": (
                    "tibber_token",
                    "tibber_home_id",
                )
            },
        ),
        ("Verification", {"fields": ("is_verified",)}),
        ("Meta", {"fields": ("id", "created_at")}),
    )

    readonly_fields = ("id", "created_at")

    # ✅ 🔥 GENAU HIER REIN
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "tibber_token" in form.base_fields:
            form.base_fields["tibber_token"].widget.attrs["size"] = 80
        return form


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "postal_code", "country", "customer_type")
    search_fields = ("user__email", "city", "postal_code", "company_name")


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "dashboard_mode", "usage_mode", "created_at")
    list_filter = ("dashboard_mode", "usage_mode")
