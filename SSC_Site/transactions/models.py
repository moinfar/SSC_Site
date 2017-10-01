from django.db import models
from mezzanine.pages.models import Page, RichText, RichTextPage
from mezzanine.forms.models import Form
from mezzanine.core.models import Orderable
from django.utils.translation import ugettext_lazy as _


class PaymentGateway(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("Gateway Type"))
    type = models.CharField(max_length=64, blank=False, null=False,
                                    default="upal", verbose_name=_("Gateway Type"))
    gateway_id = models.CharField(max_length=256, blank=False, null=False, verbose_name=_("Gateway ID"))
    gateway_api = models.CharField(max_length=512, blank=False, null=False, verbose_name=_("Gateway API"))

    class Meta:
        verbose_name = _("Price Group")
        verbose_name_plural = _("Price Groups")

    def __str__(self):
        return "{} - {}".format(self.type, self.title)


class PaymentFormPage(Page, RichText):
    payment_form = models.ForeignKey(Form, null=False, verbose_name=_("Payment Form"))
    payment_gateway = models.ForeignKey(PaymentGateway, null=False, verbose_name=_("Payment Gateway"))
    payment_description = models.CharField(max_length=256, blank=False, null=False,
                                           verbose_name=_("Payment Description"))
    capacity = models.IntegerField(default=0)
    at_full_capacity_message = models.CharField(max_length=256, blank=True, null=True,
                                                verbose_name=_("At Full Capacity Message"))

    class Meta:
        verbose_name = _("Payment Form")
        verbose_name_plural = _("Payment Forms")
        permissions = (
            ("can_view_payment_transactions", _("Can View Payment Transactions")),
        )


class PriceGroup(Orderable):
    payment_form_page = models.ForeignKey(PaymentFormPage, verbose_name=_("Containing Payment Form"))
    group_identifier = models.CharField(max_length=256, blank=False, null=False, verbose_name=_("Group Identifier"))
    payment_amount = models.BigIntegerField(verbose_name=_("Amount in Rials"))
    capacity = models.IntegerField(default=0)

    def is_full(self):
        if self.capacity == 0:
            return False
        if self.payment_form_page.payment_gateway.type == "upal":
            return UpalPaymentTransaction.objects.filter(is_payed=True, price_group=self).count() >= self.capacity

    class Meta:
        verbose_name = _("Price Group")
        verbose_name_plural = _("Price Groups")


class UpalPaymentTransaction(models.Model):
    creation_time = models.DateTimeField(blank=False, null=False, verbose_name=_("Creation Time"))
    uuid = models.CharField(max_length=512, blank=True, null=True, verbose_name=_("Form Entry UUID"))
    bank_token = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("Bank Token"))
    random_token = models.CharField(max_length=64, blank=False, null=False, verbose_name=_("Random Token"))
    price_group = models.ForeignKey(PriceGroup, blank=False, null=False, verbose_name=_("Price Group"))
    payment_amount = models.BigIntegerField(verbose_name=_("Amount in Rials"))

    is_payed = models.NullBooleanField(verbose_name=_("Is Payed"))
    payment_time = models.DateTimeField(blank=True, null=True, verbose_name=_("Payment Time"))

    class Meta:
        verbose_name = _("Upal Payment Transaction")
        verbose_name_plural = _("Upal Payment Transactions")


class ZpalPaymentTransaction(models.Model):
    creation_time = models.DateTimeField(blank=False, null=False, verbose_name=_("Creation Time"))
    uuid = models.CharField(max_length=512, blank=True, null=True, verbose_name=_("Form Entry UUID"))
    authority = models.CharField(max_length=36, blank=True, null=True, verbose_name=_("Authority"))
    price_group = models.ForeignKey(PriceGroup, blank=False, null=False, verbose_name=_("Price Group"))
    payment_amount = models.BigIntegerField(verbose_name=_("Amount in Rials"))

    is_payed = models.NullBooleanField(verbose_name=_("Is Payed"))
    ref_id = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Reference ID"))
    payment_time = models.DateTimeField(blank=True, null=True, verbose_name=_("Payment Time"))

    class Meta:
        verbose_name = _("Upal Payment Transaction")
        verbose_name_plural = _("Upal Payment Transactions")