####################
# accounts/admin.py
####################


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, UserProfile, UserSettings


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "email", "username", "is_active", "is_verified", "is_staff")
    search_fields = ("email", "username")
    ordering = ("email",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Verification", {"fields": ("is_verified",)}),
        ("Meta", {"fields": ("id", "created_at")}),
    )
    readonly_fields = ("id", "created_at")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "postal_code", "country", "customer_type")
    search_fields = ("user__email", "city", "postal_code", "company_name")


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "dashboard_mode", "usage_mode", "created_at")
    list_filter = ("dashboard_mode", "usage_mode")
