import datetime
import string
import uuid
from itertools import chain

import hashlib
import requests as web_request
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _
from mezzanine.conf import settings
from mezzanine.forms import fields
from mezzanine.forms.models import FieldEntry
from mezzanine.forms.page_processors import form_processor
from mezzanine.pages.page_processors import processor_for
from mezzanine.utils.email import split_addresses, send_mail_template
from random import choice
from zeep import Client

from ssc_template.templatetags.other_ssc_tags import is_captcha
from .models import PaymentForm, PriceGroup, UpalPaymentTransaction, ZpalPaymentTransaction


@processor_for(PaymentForm)
def payment_form_processor(request, page):
    payment_form = page.form.paymentform
    content = payment_form.content
    payment_form.send_email = False

    # TODO: This is over-dirty code! Someone please refactor this for God's sake!
    upal_transactions = get_upal_transactions_info(page)
    zpal_transactions = get_zpal_transactions_info(page)

    successful_payments = 0
    if payment_form.payment_gateway.type == "upal":
        successful_payments += upal_transactions.filter(is_payed=True).count()
    if payment_form.payment_gateway.type == "zpal":
        successful_payments += zpal_transactions.filter(is_payed=True).count()

    if payment_form.fields.filter(label="UUID").count() != 1:
        return {"status": "design_error", "content": content}

    uuid_key = "field_{}".format(payment_form.fields.get(label="UUID").id)
    if request.POST:
        mutable = request.POST._mutable
        request.POST._mutable = True
        request_uuid = uuid.uuid4()
        request.POST[uuid_key] = request_uuid
        request.POST._mutable = mutable

    form = form_processor(request, payment_form)

    if isinstance(form, dict) and "form" in form:
        if request.user.has_perm('transactions.can_view_payment_transactions'):
            if payment_form.payment_gateway.type == "upal":
                form_fields = payment_form.fields.all().order_by("id")
                captcha_indexes = [i for i, field in enumerate(form_fields) if is_captcha(field)]
                form_fields = [form_fields[i].label for i in range(len(form_fields)) if i not in captcha_indexes]
                for title in [_("Creation Time"), _("Form Entry UUID"), _("Bank Token"),
                              _("Random Token"),
                              _("Price Group"), _("Amount in Tomans"), _("Is Payed"),
                              _("Payment Time")]:
                    form_fields.append(title)
                upal_transactions.filter(
                    creation_time__lt=timezone.now() - datetime.timedelta(minutes=20),
                    is_payed=None).update(is_payed=False)
                successful_transactions = upal_transactions.filter(is_payed=True)
                pending_transactions = upal_transactions.filter(is_payed=None)
                failed_transactions = upal_transactions.filter(is_payed=False)
                transactions = chain(successful_transactions, pending_transactions,
                                     failed_transactions)
                transactions_info = []
                for transaction in transactions:
                    entries = get_transaction_entries(transaction)
                    if entries is not None:
                        entries = [entry.value for i, entry in enumerate(entries) if i not in captcha_indexes]
                        for value in [transaction.creation_time, transaction.uuid,
                                      transaction.bank_token,
                                      transaction.random_token,
                                      transaction.price_group.group_identifier + " (" + str(
                                          transaction.price_group.payment_amount) + ")",
                                      transaction.payment_amount,
                                      transaction.is_payed, transaction.payment_time]:
                            entries.append(value)
                        transactions_info.append(entries)

            if payment_form.payment_gateway.type == "zpal":
                form_fields = payment_form.fields.all().order_by("id")
                captcha_indexes = [i for i, field in enumerate(form_fields) if is_captcha(field)]
                form_fields = [form_fields[i].label for i in range(len(form_fields)) if i not in captcha_indexes]
                for title in [_("Creation Time"), _("Form Entry UUID"), _("Authority"),
                              _("Price Group"),
                              _("Amount in Tomans"), _("Is Payed"), _("Reference ID"),
                              _("Payment Time")]:
                    form_fields.append(title)
                zpal_transactions.filter(
                    creation_time__lt=timezone.now() - datetime.timedelta(minutes=20),
                    is_payed=None).update(is_payed=False)
                successful_transactions = zpal_transactions.filter(is_payed=True)
                pending_transactions = zpal_transactions.filter(is_payed=None)
                failed_transactions = zpal_transactions.filter(is_payed=False)
                transactions = chain(successful_transactions, pending_transactions,
                                     failed_transactions)
                transactions_info = []
                for transaction in transactions:
                    entries = get_transaction_entries(transaction)
                    if entries is not None:
                        entries = [entry.value for i, entry in enumerate(entries) if i not in captcha_indexes]
                        for value in [transaction.creation_time, transaction.uuid,
                                      transaction.authority,
                                      transaction.price_group.group_identifier + " (" + str(
                                          transaction.price_group.payment_amount) + ")",
                                      transaction.payment_amount,
                                      transaction.is_payed, transaction.ref_id,
                                      transaction.payment_time]:
                            entries.append(value)
                        transactions_info.append(entries)

            return {"status": "form", "form": form["form"], "payment_form": payment_form,
                    "form_fields": form_fields, "transactions_info": transactions_info,
                    "content": content}

        if payment_form.capacity != 0:
            if successful_payments >= payment_form.capacity:
                return {"status": "at_full_capacity", "content": content}

        return {"status": "form", "form": form["form"], "payment_form": payment_form,
                "content": content}

    plan = PriceGroup.objects.get(id=request.POST.get("payment_plan_id"))
    if plan.capacity != 0:
        plan_successful_payments = 0
        if payment_form.payment_gateway.type == "upal":
            plan_successful_payments += upal_transactions.filter(is_payed=True,
                                                                 price_group=plan).count()
        if payment_form.payment_gateway.type == "zpal":
            plan_successful_payments += zpal_transactions.filter(is_payed=True,
                                                                 price_group=plan).count()

        if plan_successful_payments >= plan.capacity:
            return {"status": "at_full_capacity", "content": content}

    if payment_form.payment_gateway.type == "upal":
        transaction = new_upal_payment(request, payment_form, plan, request_uuid)
    if payment_form.payment_gateway.type == "zpal":
        transaction = new_zpal_payment(request, payment_form, plan, request_uuid)

    if transaction is None:
        return {"status": "gateway_error", "content": content}

    if payment_form.payment_gateway.type == "upal":
        # payment_url = 'https://upal.ir/transaction/submit?id={}'.format(transaction.bank_token)
        payment_url = 'http://salam.im/transaction/submit?id={}'.format(transaction.bank_token)
    if payment_form.payment_gateway.type == "zpal":
        payment_url = 'https://www.zarinpal.com/pg/StartPay/{}'.format(transaction.authority)

    if payment_form.capacity != 0:
        if payment_form.payment_gateway.type == "upal":
            pending_payments = successful_payments + upal_transactions.filter(
                is_payed=None,
                creation_time__gt=timezone.now() - datetime.timedelta(minutes=10)).count()
        if payment_form.payment_gateway.type == "zpal":
            pending_payments = successful_payments + zpal_transactions.filter(
                is_payed=None,
                creation_time__gt=timezone.now() - datetime.timedelta(minutes=10)).count()
        if pending_payments > payment_form.capacity:
            return {"status": "payment", "payment_url": payment_url, "warning": "reserved_list",
                    "content": content}

    if plan.capacity != 0:
        if payment_form.payment_gateway.type == "upal":
            plan_pending_payments = plan_successful_payments + upal_transactions.filter(
                is_payed=None, creation_time__gt=timezone.now() - datetime.timedelta(minutes=10),
                price_group=plan).count()
        if payment_form.payment_gateway.type == "zpal":
            plan_pending_payments = plan_successful_payments + zpal_transactions.filter(
                is_payed=None, creation_time__gt=timezone.now() - datetime.timedelta(minutes=10),
                price_group=plan).count()
        if plan_pending_payments > plan.capacity:
            return {"status": "payment", "payment_url": payment_url, "warning": "reserved_list",
                    "content": content}

    return {"status": "payment", "payment_url": payment_url, "content": content}


def new_upal_payment(request, payment_form, plan, request_uuid):
    random_token = ''.join(
        choice(string.lowercase + string.uppercase + string.digits) for i in range(16))
    transaction = UpalPaymentTransaction(creation_time=timezone.now(),
                                         uuid=request_uuid,
                                         random_token=random_token,
                                         price_group=plan,
                                         payment_amount=plan.payment_amount)
    transaction.save()
    return_url = request.build_absolute_uri(
        reverse('transactions_from_bank', args=('upal', transaction.id)))
    try:
        # payment_request = web_request.post("https://upal.ir//transaction/create",
        payment_request = web_request.post("http://salam.im//transaction/create",
                                           data={
                                               'gateway_id': payment_form.payment_gateway.gateway_id,
                                               'amount': plan.payment_amount,
                                               'description': "{}-{}".format(
                                                   payment_form.payment_description,
                                                   plan.group_identifier),
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


def new_zpal_payment(request, payment_form, plan, request_uuid):
    transaction = ZpalPaymentTransaction(creation_time=timezone.now(),
                                         uuid=request_uuid,
                                         price_group=plan,
                                         payment_amount=plan.payment_amount)
    transaction.save()
    return_url = request.build_absolute_uri(
        reverse('transactions_from_bank', args=('zpal', transaction.id)))
    try:
        client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
        payment_parameters = {
            'MerchantID': payment_form.payment_gateway.gateway_id,
            'Amount': plan.payment_amount / 10,
            'Description': "{}-{}".format(payment_form.payment_description,
                                          plan.group_identifier),
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


def get_transaction_entries(transaction):
    if FieldEntry.objects.filter(value=transaction.uuid).count() == 1:
        entry = FieldEntry.objects.get(value=transaction.uuid).entry
        field_entries = FieldEntry.objects.filter(entry=entry).order_by("field_id")
        return field_entries
    return None


def from_bank(request, transaction_type, transaction_id):
    ret = None

    if transaction_type == 'upal':
        transaction = UpalPaymentTransaction.objects.get(id=transaction_id)
        ret = from_bank_upal(request, transaction)
    if transaction_type == 'zpal':
        transaction = ZpalPaymentTransaction.objects.get(id=transaction_id)
        ret = from_bank_zpal(request, transaction)
    return ret or render(request, 'pages/error.html',
                         {"page": transaction.price_group.payment_for,
                          "title": _("UnSuccessful Payment Transaction")})


def from_bank_upal(request, transaction):
    bank_token = request.GET.get('trans_id')
    validation_hash = request.GET.get('valid')
    if bank_token == transaction.bank_token:
        our_validation_md5 = hashlib.md5()
        our_validation_md5.update(
            "{}{}{}{}".format(transaction.price_group.payment_for.payment_gateway.gateway_id,
                              transaction.payment_amount,
                              transaction.price_group.payment_for.payment_gateway.gateway_api,
                              transaction.random_token).encode())
        if our_validation_md5.hexdigest() == validation_hash:

            send_payment_main = False
            if transaction.is_payed is None or transaction.is_payed is False:
                transaction.is_payed = True
                transaction.payment_time = timezone.now()
                transaction.save()

                send_payment_main = True

            form = transaction.price_group.payment_for.payment_form
            form_fields = form.fields.all().order_by("id")

            field_entries = get_transaction_entries(transaction)

            email_from = form.email_from or settings.DEFAULT_FROM_EMAIL

            field_tuples = []
            email_to = None
            for field, field_entry in zip(form_fields, field_entries):
                field_tuples.append((field.label, field_entry.value))
                if field.is_a(fields.EMAIL):
                    email_to = field_entry.value

            field_tuples.append((_('Price Group'), transaction.price_group.group_identifier))
            field_tuples.append((_('Payment in Tomans'), transaction.payment_amount))

            subject = form.email_subject

            context = {
                "fields": field_tuples,
                "message": form.email_message,
                "request": request,
            }

            if send_payment_main:
                send_mail_template(subject, "email/form_response", email_from, email_to, context)

                email_copies = split_addresses(form.email_copies)
                if email_copies:
                    send_mail_template(subject, "email/form_response_copies",
                                       email_from, email_copies, context)

            return render(request, 'pages/message.html',
                          {"page": transaction.price_group.payment_for,
                           "title": _("Successful Payment Transaction"),
                           "context": context})
        else:
            # print(our_validation_md5.hexdigest())
            # print(validation_hash)
            transaction.is_payed = False
            transaction.save()


def from_bank_zpal(request, transaction):
    authority = request.GET.get('Authority')
    if authority == transaction.authority:
        client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
        validation_parameters = {
            'MerchantID': transaction.price_group.payment_for.payment_gateway.gateway_id,
            'Authority': authority,
            'Amount': transaction.payment_amount / 10,
        }
        validation_request = client.service.PaymentVerification(**validation_parameters)

        if validation_request.Status == 100:

            send_payment_main = False
            if transaction.is_payed is None or transaction.is_payed is False:
                transaction.is_payed = True
                transaction.payment_time = timezone.now()
                transaction.ref_id = validation_request.RefID
                transaction.save()

                send_payment_main = True

            form = transaction.price_group.payment_for.payment_form
            form_fields = form.fields.all().order_by("id")

            field_entries = get_transaction_entries(transaction)

            email_from = form.email_from or settings.DEFAULT_FROM_EMAIL

            field_tuples = []
            email_to = None
            for field, field_entry in zip(form_fields, field_entries):
                field_tuples.append((field.label, field_entry.value))
                if field.is_a(fields.EMAIL):
                    email_to = field_entry.value

            field_tuples.append((_('Price Group'), transaction.price_group.group_identifier))
            field_tuples.append((_('Payment in Tomans'), transaction.payment_amount))

            subject = form.email_subject

            context = {
                "fields": field_tuples,
                "message": form.email_message,
                "request": request,
            }

            if send_payment_main:
                send_mail_template(subject, "email/form_response", email_from, email_to, context)

                email_copies = split_addresses(form.email_copies)
                if email_copies:
                    send_mail_template(subject, "email/form_response_copies",
                                       email_from, email_copies, context)

            return render(request, 'pages/message.html',
                          {"page": transaction.price_group.payment_for,
                           "title": _("Successful Payment Transaction"),
                           "context": context})
        else:
            # print(our_validation_md5.hexdigest())
            # print(validation_hash)
            transaction.is_payed = False
            transaction.save()


def get_upal_transactions_info(page):
    transactions = UpalPaymentTransaction.objects.filter(
        price_group__payment_form=page)
    return transactions


def get_zpal_transactions_info(page):
    transactions = ZpalPaymentTransaction.objects.filter(
        price_group__payment_form=page)
    return transactions
