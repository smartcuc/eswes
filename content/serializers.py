########################
# content/serializers.py
########################

from rest_framework import serializers
from .models import TenantPage, PageBlock


class PageBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBlock
        fields = ("id", "block_type", "content", "order")


class TenantPageSerializer(serializers.ModelSerializer):
    blocks = PageBlockSerializer(many=True, read_only=True)

    class Meta:
        model = TenantPage
        fields = ("id", "title", "slug", "blocks")
