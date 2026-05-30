#################
# market/admin.py
#################


from django.contrib import admin
from .models import SpotPrice


@admin.register(SpotPrice)
class SpotPriceAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "price_eur_per_kwh", "source", "created_at")
    list_filter = ("source",)
    search_fields = ("source",)
