import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from mezzanine.core.models import Orderable
from mezzanine.forms.models import Form, FieldEntry
from polymorphic.models import PolymorphicModel


class PaymentGateway(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False,
                             verbose_name=_("Gateway Type"))
    type = models.CharField(max_length=64, blank=False, null=False,
                            default="zpal", verbose_name=_("Gateway Type"))
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

    @property
    def is_full(self):
        if self.capacity == -1:
            return False
        successful_payments = self.payment_transactions.filter(is_paid=True).count()
        pending_payments = successful_payments + self.payment_transactions.filter(
            is_paid=None, creation_time__gt=timezone.now() - datetime.timedelta(minutes=10),
            price_group=self).count()
        return pending_payments >= self.capacity

    class Meta:
        verbose_name = _("Price Group")
        verbose_name_plural = _("Price Groups")


class PaymentTransaction(PolymorphicModel):
    creation_time = models.DateTimeField(blank=False, null=False, verbose_name=_("Creation Time"))
    uuid = models.CharField(max_length=512, blank=True, null=True,
                            verbose_name=_("Form Entry UUID"))
    price_group = models.ForeignKey(PriceGroup, blank=False, null=False,
                                    verbose_name=_("Price Group"),
                                    related_name='payment_transactions')
    payment_amount = models.BigIntegerField(verbose_name=_("Amount in Tomans"))
    is_paid = models.NullBooleanField(verbose_name=_("Is Paid"))
    payment_time = models.DateTimeField(blank=True, null=True, verbose_name=_("Payment Time"))

    class Meta:
        abstract = True

    def get_transaction_entries(self):
        if FieldEntry.objects.filter(value=self.uuid).count() == 1:
            entry = FieldEntry.objects.get(value=self.uuid).entry
            field_entries = FieldEntry.objects.filter(entry=entry).order_by("field_id")
            return field_entries
        return None

    @classmethod
    def new_payment_transaction(cls, request, payment_form, plan, request_uuid):
        raise NotImplementedError()

    def get_payment_url(self):
        raise NotImplementedError()

    def from_bank(self, request):
        raise NotImplementedError()
