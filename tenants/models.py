###################
# tenants/models.py
###################

import uuid
from django.db import models
from django.utils.text import slugify


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    # 🔥 NEU: Theme Felder
    primary_color = models.CharField(max_length=50, default="from-orange-400")
    secondary_color = models.CharField(max_length=50, default="to-orange-600")
    button_color = models.CharField(max_length=50, default="bg-orange-500")

    def __str__(self):
        return self.name
