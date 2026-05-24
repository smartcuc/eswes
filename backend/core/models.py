import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=200)
    timezone = models.CharField(_("Timezone"), max_length=64, default="Europe/Berlin")
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Tenant")
        verbose_name_plural = _("Tenants")

    def __str__(self):
        return self.name


class Customer(models.Model):
    """
    Vertragspartner (Privat/Unternehmen). Kann mehrere User-Accounts haben.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="customers",
        verbose_name=_("Tenant"),
    )
    name = models.CharField(_("Name"), max_length=200)
    email = models.EmailField(_("Email"), blank=True, null=True)
    external_ref = models.CharField(
        _("External reference"), max_length=128, blank=True, null=True
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        indexes = [
            models.Index(fields=["tenant", "name"], name="idx_customer_tenant_name")
        ]

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    class Role(models.TextChoices):
        TENANT_ADMIN = "TENANT_ADMIN", _("Tenant admin")
        COMMUNITY_ADMIN = "COMMUNITY_ADMIN", _("Community admin")
        MEMBER = "MEMBER", _("Member")
        BILLING = "BILLING", _("Billing")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("User"),
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="user_profiles",
        verbose_name=_("Tenant"),
    )
    role = models.CharField(
        _("Role"), max_length=32, choices=Role.choices, default=Role.MEMBER
    )

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")

    def __str__(self):
        return f"{self.user} ({self.role})"
