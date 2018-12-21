import hashlib
import string

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from mezzanine.utils.email import send_mail_template, split_addresses
from django.shortcuts import render
from random import choice
import requests as web_request
from zeep import Client

from django.db import models
from django.utils.translation import ugettext_lazy as _
from mezzanine.forms import fields

from transactions.models import PaymentTransaction


def get_transaction_class(type):
    if type == "upal":
        return UpalPaymentTransaction
    if type == "zpal":
        return ZpalPaymentTransaction


# Subclasses of PaymentTransaction are placed here for more readability

class UpalPaymentTransaction(PaymentTransaction):
    bank_token = models.CharField(max_length=256, blank=True, null=True,
                                  verbose_name=_("Bank Token"))
    random_token = models.CharField(max_length=64, blank=False, null=False,
                                    verbose_name=_("Random Token"))

    class Meta:
        verbose_name = _("Zpal Payment Transaction")
        verbose_name_plural = _("Zpal Payment Transactions")

    @classmethod
    def new_payment_transaction(cls, request, payment_form, price_group, discount_code, payment_amount, request_uuid):
        random_token = ''.join(choice(string.ascii_letters + string.digits) for _ in range(16))
        transaction = UpalPaymentTransaction(creation_time=timezone.now(),
                                             uuid=request_uuid,
                                             random_token=random_token,
                                             price_group=price_group,
                                             discount_code=discount_code,
                                             payment_amount=payment_amount or price_group.payment_amount)
        transaction.save()
        return_url = request.build_absolute_uri(
            reverse('transactions_from_bank', args=('upal', transaction.id)))
        try:
            payment_request = web_request.post("http://salam.im//transaction/create",
                                               data={
                                                   'gateway_id': payment_form.payment_gateway.gateway_id,
                                                   'amount': (payment_amount or price_group.payment_amount) * 10,
                                                   'description': "{}-{}".format(
                                                       payment_form.payment_description,
                                                       price_group.group_identifier),
                                                   'rand': random_token,
                                                   'redirect_url': return_url,
                                               })
        except web_request.ConnectionError:
            transaction.delete()
            return None

        if not (payment_request.status_code == 200 and payment_request.reason == 'OK'):
            return None
        transaction.bank_token = payment_request.text
        transaction.save()

        return transaction

    def get_payment_url(self):
        return 'http://salam.im/transaction/submit?id={}'.format(self.bank_token)

    def from_bank(self, request):
        bank_token = request.GET.get('trans_id')
        validation_hash = request.GET.get('valid')
        if bank_token == self.bank_token:
            our_validation_md5 = hashlib.md5()
            our_validation_md5.update(
                "{}{}{}{}".format(self.price_group.payment_form.payment_gateway.gateway_id,
                                  self.payment_amount * 10,
                                  self.price_group.payment_form.payment_gateway.gateway_api,
                                  self.random_token).encode())
            if our_validation_md5.hexdigest() == validation_hash:

                send_payment_main = False
                if self.is_paid is None or self.is_paid is False:
                    self.is_paid = True
                    self.payment_time = timezone.now()
                    self.save()

                    send_payment_main = True

                form = self.price_group.payment_form.payment_form
                form_fields = form.fields.all().order_by("id")

                field_entries = self.get_transaction_entries(self)

                email_from = form.email_from or settings.DEFAULT_FROM_EMAIL

                field_tuples = []
                email_to = None
                for field, field_entry in zip(form_fields, field_entries):
                    field_tuples.append((field, field_entry.value))
                    if field.is_a(fields.EMAIL):
                        email_to = field_entry.value

                field_tuples.append((_('Price Group'), self.price_group.group_identifier))
                field_tuples.append((_('Payment Amount in Tomans'), self.payment_amount))

                subject = form.email_subject

                context = {
                    "fields": field_tuples,
                    "message": form.email_message,
                    "request": request,
                    "site_url": settings.SITE_URL,
                }

                if send_payment_main:
                    send_mail_template(subject, "email/form_response", email_from, email_to,
                                       context)

                    email_copies = split_addresses(form.email_copies)
                    if email_copies:
                        send_mail_template(subject, "email/form_response_copies",
                                           email_from, email_copies, context)

                return render(request, 'pages/message.html',
                              {"page": self.price_group.payment_form,
                               "title": _("Successful Payment Transaction"),
                               "context": context})
            else:
                self.is_paid = False
                self.save()


class ZpalPaymentTransaction(PaymentTransaction):
    authority = models.CharField(max_length=36, blank=True, null=True, verbose_name=_("Authority"))
    ref_id = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Reference ID"))

    class Meta:
        verbose_name = _("Upal Payment Transaction")
        verbose_name_plural = _("Upal Payment Transactions")

    @classmethod
    def new_payment_transaction(cls, request, payment_form, price_group, discount_code, payment_amount, request_uuid):
        transaction = ZpalPaymentTransaction(creation_time=timezone.now(),
                                             uuid=request_uuid,
                                             price_group=price_group,
                                             discount_code=discount_code,
                                             payment_amount=payment_amount or price_group.payment_amount)
        transaction.save()
        return_url = request.build_absolute_uri(
            reverse('transactions_from_bank', args=('zpal', transaction.id)))
        try:
            client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
            payment_parameters = {
                'MerchantID': payment_form.payment_gateway.gateway_id,
                'Amount': payment_amount or price_group.payment_amount,
                'Description': "{}-{}".format(payment_form.payment_description,
                                              price_group.group_identifier),
                'CallbackURL': return_url,
            }
            payment_request = client.service.PaymentRequest(**payment_parameters)

        except:
            transaction.delete()
            return None

        if not payment_request.Status == 100:
            return None
        transaction.authority = payment_request.Authority
        transaction.save()

        return transaction

    def get_payment_url(self):
        return 'https://www.zarinpal.com/pg/StartPay/{}'.format(self.authority)

    def from_bank(self, request):
        authority = request.GET.get('Authority')
        if authority == self.authority:
            if self.is_paid:
                return
            client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
            validation_parameters = {
                'MerchantID': self.price_group.payment_form.payment_gateway.gateway_id,
                'Authority': authority,
                'Amount': self.payment_amount,
            }
            validation_request = client.service.PaymentVerification(**validation_parameters)

            if validation_request.Status == 100:

                send_payment_main = False
                if self.is_paid is None or self.is_paid is False:
                    self.is_paid = True
                    self.payment_time = timezone.now()
                    self.ref_id = validation_request.RefID
                    self.save()

                    send_payment_main = True

                form = self.price_group.payment_form
                form_fields = form.fields.all().order_by("id")

                field_entries = self.get_transaction_entries()

                email_from = form.email_from or settings.DEFAULT_FROM_EMAIL

                field_tuples = []
                email_to = None
                for field, field_entry in zip(form_fields, field_entries):
                    field_tuples.append((field, field_entry.value))
                    if field.is_a(fields.EMAIL):
                        email_to = field_entry.value

                field_tuples.append((_('Price Group'), self.price_group.group_identifier))
                field_tuples.append((_('Payment Amount in Tomans'), self.payment_amount))

                subject = form.email_subject

                context = {
                    "fields": field_tuples,
                    "message": form.email_message,
                    "request": request,
                    "site_url": settings.SITE_URL,
                }

                if send_payment_main:
                    send_mail_template(subject, "email/form_response", email_from, email_to,
                                       context)

                    email_copies = split_addresses(form.email_copies)
                    if email_copies:
                        send_mail_template(subject, "email/form_response_copies",
                                           email_from, email_copies, context)

                return render(request, 'pages/message.html',
                              {"page": self.price_group.payment_form,
                               "title": _("Successful Payment Transaction"),
                               "context": context})
            else:
                self.is_paid = False
                self.save()
