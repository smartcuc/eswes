import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tariff(models.Model):
    class PricingModel(models.TextChoices):
        FIXED = "FIXED", _("Fixed")
        TIME_OF_USE = "TIME_OF_USE", _("Time of use")
        DYNAMIC = "DYNAMIC", _("Dynamic / Indexed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="tariffs",
        verbose_name=_("Tenant"),
    )
    name = models.CharField(_("Name"), max_length=200)
    currency = models.CharField(_("Currency"), max_length=8, default="EUR")
    pricing_model = models.CharField(
        _("Pricing model"),
        max_length=32,
        choices=PricingModel.choices,
        default=PricingModel.FIXED,
    )
    base_fee_monthly = models.DecimalField(
        _("Base fee monthly"), max_digits=12, decimal_places=2, default=0
    )
    config = models.JSONField(_("Config"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Tariff")
        verbose_name_plural = _("Tariffs")


class BillingPeriod(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", _("Open")
        CLOSED = "CLOSED", _("Closed")
        INVOICED = "INVOICED", _("Invoiced")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="billing_periods",
        verbose_name=_("Tenant"),
    )
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))
    status = models.CharField(
        _("Status"), max_length=16, choices=Status.choices, default=Status.OPEN
    )

    class Meta:
        verbose_name = _("Billing period")
        verbose_name_plural = _("Billing periods")
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "start_date", "end_date"], name="uniq_period_range"
            ),
        ]


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        ISSUED = "ISSUED", _("Issued")
        PAID = "PAID", _("Paid")
        CANCELED = "CANCELED", _("Canceled")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name=_("Tenant"),
    )
    customer = models.ForeignKey(
        "core.Customer",
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name=_("Customer"),
    )
    period = models.ForeignKey(
        BillingPeriod,
        on_delete=models.PROTECT,
        related_name="invoices",
        verbose_name=_("Billing period"),
    )

    status = models.CharField(
        _("Status"), max_length=16, choices=Status.choices, default=Status.DRAFT
    )
    total_net = models.DecimalField(
        _("Total net"), max_digits=14, decimal_places=2, default=0
    )
    tax = models.DecimalField(_("Tax"), max_digits=14, decimal_places=2, default=0)
    total_gross = models.DecimalField(
        _("Total gross"), max_digits=14, decimal_places=2, default=0
    )

    issued_at = models.DateTimeField(_("Issued at"), null=True, blank=True)
    due_at = models.DateTimeField(_("Due at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")


class InvoiceLine(models.Model):
    class LineType(models.TextChoices):
        ENERGY = "ENERGY", _("Energy")
        CREDIT = "CREDIT", _("Credit")
        BASE_FEE = "BASE_FEE", _("Base fee")
        TAX = "TAX", _("Tax")
        ADJUSTMENT = "ADJUSTMENT", _("Adjustment")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Invoice"),
    )
    line_type = models.CharField(
        _("Line type"), max_length=16, choices=LineType.choices
    )
    description = models.CharField(
        _("Description"), max_length=255, blank=True, default=""
    )
    quantity_kwh = models.DecimalField(
        _("Quantity (kWh)"), max_digits=14, decimal_places=6, null=True, blank=True
    )
    unit_price = models.DecimalField(
        _("Unit price"), max_digits=14, decimal_places=6, default=0
    )
    amount = models.DecimalField(
        _("Amount"), max_digits=14, decimal_places=2, default=0
    )
