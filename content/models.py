###################
# content/models.py
###################

from django.db import models
from core.models import Tenant


class TenantPage(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="pages")

    title = models.CharField(max_length=255)
    slug = models.SlugField()

    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("tenant", "slug")

    def __str__(self):
        return f"{self.title} ({self.tenant})"


# ----------------------------------------------------------------#

BLOCK_TYPES = [
    ("hero", "Hero"),
    ("text", "Text"),
    ("image", "Image"),
    ("cta", "Call To Action"),
    ("sankey", "Sankey"),
]


class PageBlock(models.Model):
    page = models.ForeignKey(
        TenantPage, on_delete=models.CASCADE, related_name="blocks"
    )

    block_type = models.CharField(max_length=50, choices=BLOCK_TYPES)

    content = models.JSONField()

    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.block_type} ({self.order})"


class Meta:
    ordering = ["order"]
