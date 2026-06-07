##################
# content/admin.py
##################

from django.contrib import admin
from .models import TenantPage, PageBlock


class PageBlockInline(admin.TabularInline):
    model = PageBlock
    extra = 1
    ordering = ("order",)


@admin.register(TenantPage)
class TenantPageAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "is_public", "updated_at")
    list_filter = ("tenant", "is_public")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PageBlockInline]
