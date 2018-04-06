import datetime

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.deletion import SET_NULL
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
        verbose_name = _("Payment Gateway")
        verbose_name_plural = _("Payment Gateways")

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

    @property
    def has_discount_code(self):
        for price_group in self.price_groups.all():
            if price_group.discount_codes.count():
                return True
        return False


class PriceGroup(Orderable):
    payment_form = models.ForeignKey(PaymentForm, verbose_name=_("Containing Payment Form"),
                                     related_name='price_groups')
    group_identifier = models.CharField(max_length=256, blank=False, null=False,
                                        verbose_name=_("Group Identifier"))
    payment_amount = models.BigIntegerField(verbose_name=_("Amount in Tomans"), validators=[MinValueValidator(100)])
    capacity = models.IntegerField(default=-1, help_text=_("Enter -1 for infinite capacity"))

    class Meta:
        verbose_name = _("Price Group")
        verbose_name_plural = _("Price Groups")

    def __str__(self):
        return '{} of payment form: {}'.format(self.group_identifier, self.payment_form)

    @property
    def is_full(self):
        if self.capacity == -1:
            return False
        return self.get_pending_payments().count() >= self.capacity

    def get_pending_payments(self):
        return self.payment_transactions.filter(Q(is_paid=True) | Q(is_paid=None, creation_time__gt=timezone.now() - datetime.timedelta(minutes=10)))

    def validate_discount_code(self, code):
        try:
            discount_code = self.discount_codes.get(code=code)
        except ObjectDoesNotExist:
            return {'error': _('The provided discount code is invalid')}
        if discount_code.capacity != -1:
            if self.get_pending_payments().filter(discount_code=code).count() >= discount_code.capacity:
                return {'error': _('Unfortunately capacity of this code is full')}

        return {'new_price': discount_code.new_price}


class DiscountCode(models.Model):
    code = models.CharField(max_length=20, verbose_name=_("Discount Code"))
    price_group = models.ForeignKey(to=PriceGroup, verbose_name=_("Price Group"),
                                    related_name='discount_codes')
    capacity = models.IntegerField(default=-1, help_text=_("Enter -1 for infinite capacity"))
    discount_percentage = models.PositiveIntegerField(validators=[MaxValueValidator(100)])

    class Meta:
        unique_together = ('code', 'price_group')

    def __str__(self):
        return '{} for {}'.format(self.code, self.price_group)

    @property
    def new_price(self):
        return self.price_group.payment_amount * (100 - self.discount_percentage) / 100


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
    discount_code = models.CharField(max_length=20, verbose_name=_("Discount Code"), null=True, blank=True)

    class Meta:
        abstract = True

    def get_transaction_entries(self):
        if FieldEntry.objects.filter(value=self.uuid).count() == 1:
            entry = FieldEntry.objects.get(value=self.uuid).entry
            field_entries = FieldEntry.objects.filter(entry=entry).order_by("field_id")
            return field_entries
        return None

    @classmethod
    def new_payment_transaction(cls, request, payment_form, price_group, discount_code, payment_amount, request_uuid):
        raise NotImplementedError()

    def get_payment_url(self):
        raise NotImplementedError()

    def from_bank(self, request):
        raise NotImplementedError()
