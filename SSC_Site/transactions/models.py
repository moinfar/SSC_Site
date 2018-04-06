from django.db import models
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.models import Orderable
from mezzanine.forms.models import Form
from mezzanine.pages.models import Page, RichText
from polymorphic.models import PolymorphicModel


class PaymentGateway(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False,
                             verbose_name=_("Gateway Type"))
    type = models.CharField(max_length=64, blank=False, null=False,
                            default="upal", verbose_name=_("Gateway Type"))
    gateway_id = models.CharField(max_length=256, blank=False, null=False,
                                  verbose_name=_("Gateway ID"))
    gateway_api = models.CharField(max_length=512, blank=False, null=False,
                                   verbose_name=_("Gateway API"))

    class Meta:
        verbose_name = _("Price Group")
        verbose_name_plural = _("Price Groups")

    def __str__(self):
        return "{} - {}".format(self.type, self.title)


class PaymentForm(Form):
    payment_gateway = models.ForeignKey(PaymentGateway, null=False,
                                        verbose_name=_("Payment Gateway"))
    payment_description = models.CharField(max_length=256, blank=False, null=False,
                                           verbose_name=_("Payment Description"))
    capacity = models.IntegerField(default=-1, help_text=_("Enter -1 for infinite capacity"))
    at_full_capacity_message = models.CharField(max_length=256, blank=True, null=True,
                                                verbose_name=_("At Full Capacity Message"))

    class Meta:
        verbose_name = _("Payment Form")
        verbose_name_plural = _("Payment Forms")
        permissions = (
            ("can_view_payment_transactions", _("Can View Payment Transactions")),
        )

    def get_content_model(self):
        return 'paymentform'


class PriceGroup(Orderable):
    payment_form = models.ForeignKey(PaymentForm, verbose_name=_("Containing Payment Form"))
    group_identifier = models.CharField(max_length=256, blank=False, null=False,
                                        verbose_name=_("Group Identifier"))
    payment_amount = models.BigIntegerField(verbose_name=_("Amount in Tomans"))
    capacity = models.IntegerField(default=-1, help_text=_("Enter -1 for infinite capacity"))

    def is_full(self):
        if self.capacity == 0:
            return False
        if self.payment_form.payment_gateway.type == "upal":
            return UpalPaymentTransaction.objects.filter(is_payed=True,
                                                         price_group=self).count() >= self.capacity

    class Meta:
        verbose_name = _("Price Group")
        verbose_name_plural = _("Price Groups")


class PaymentTransaction(PolymorphicModel):
    creation_time = models.DateTimeField(blank=False, null=False, verbose_name=_("Creation Time"))
    uuid = models.CharField(max_length=512, blank=True, null=True,
                        verbose_name=_("Form Entry UUID"))
    price_group = models.ForeignKey(PriceGroup, blank=False, null=False,
                                    verbose_name=_("Price Group"), related_name=_('Payment_Transactions'))
    payment_amount = models.BigIntegerField(verbose_name=_("Amount in Tomans"))
    is_payed = models.NullBooleanField(verbose_name=_("Is Payed"))
    payment_time = models.DateTimeField(blank=True, null=True, verbose_name=_("Payment Time"))

    class Meta:
        abstract = True


class UpalPaymentTransaction(PaymentTransaction):
    bank_token = models.CharField(max_length=256, blank=True, null=True,
                                  verbose_name=_("Bank Token"))
    random_token = models.CharField(max_length=64, blank=False, null=False,
                                    verbose_name=_("Random Token"))


    class Meta:
        verbose_name = _("Upal Payment Transaction")
        verbose_name_plural = _("Upal Payment Transactions")


class ZpalPaymentTransaction(PaymentTransaction):
    authority = models.CharField(max_length=36, blank=True, null=True, verbose_name=_("Authority"))
    price_group = models.ForeignKey(PriceGroup, blank=False, null=False,
                                    verbose_name=_("Price Group"))

    ref_id = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Reference ID"))

    class Meta:
        verbose_name = _("Upal Payment Transaction")
        verbose_name_plural = _("Upal Payment Transactions")
