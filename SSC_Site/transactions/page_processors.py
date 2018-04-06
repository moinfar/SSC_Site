import datetime
import uuid
from itertools import chain

from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _
from mezzanine.forms.page_processors import form_processor
from mezzanine.pages.page_processors import processor_for

from ssc_template.templatetags.other_ssc_tags import is_captcha
from transactions.payment_transaction import UpalPaymentTransaction, ZpalPaymentTransaction, \
    get_transaction_class
from .models import PaymentForm, PriceGroup


@processor_for(PaymentForm)
def payment_form_processor(request, page):
    payment_form = page.form.paymentform
    content = payment_form.content
    payment_form.send_email = False

    transaction_class = get_transaction_class(payment_form.payment_gateway.type)

    transactions = transaction_class.objects.filter(price_group__payment_form=page)
    successful_payments = transactions.filter(is_payed=True).count()

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
            form_fields = payment_form.fields.all().order_by("id")
            captcha_indexes = [i for i, field in enumerate(form_fields) if is_captcha(field)]
            form_fields = [form_fields[i].label for i in range(len(form_fields)) if
                           i not in captcha_indexes]

            headers = [_("Creation Time"), _("Price Group"), _("Amount in Tomans"),
                       _("Is Payed"), _("Payment Time")]
            if transaction_class == UpalPaymentTransaction:
                headers.append(_("Bank Token"))
            elif transaction_class == ZpalPaymentTransaction:
                headers.append(_("Reference ID"))
            for title in headers:
                form_fields.append(title)
            transactions.filter(
                creation_time__lt=timezone.now() - datetime.timedelta(minutes=20),
                is_payed=None).update(is_payed=False)
            successful_transactions = transactions.filter(is_payed=True)
            pending_transactions = transactions.filter(is_payed=None)
            failed_transactions = transactions.filter(is_payed=False)
            transactions = chain(successful_transactions, pending_transactions,
                                 failed_transactions)
            transactions_info = []
            for transaction in transactions:
                entries = transaction.get_transaction_entries()
                if entries is not None:
                    entries = [entry.value for i, entry in enumerate(entries) if
                               i not in captcha_indexes]

                    values = [
                        transaction.creation_time,
                        transaction.price_group.group_identifier + " (" + str(transaction.price_group.payment_amount) + ")",
                        transaction.payment_amount,
                        transaction.is_payed,
                        transaction.payment_time,
                    ]

                    if type(transaction) == UpalPaymentTransaction:
                        values.append(transaction.bank_token)
                    elif type(transaction) == ZpalPaymentTransaction:
                        values.append(transaction.ref_id)

                    for value in values:
                        entries.append(value)
                    transactions_info.append(entries)

            return {"status": "form", "form": form["form"], "payment_form": payment_form,
                    "form_fields": form_fields, "transactions_info": transactions_info,
                    "content": content}

        if payment_form.capacity != -1:
            if successful_payments >= payment_form.capacity:
                return {"status": "at_full_capacity", "content": content}

        return {"status": "form", "form": form["form"], "payment_form": payment_form,
                "content": content}

    plan = PriceGroup.objects.get(id=request.POST.get("payment_plan_id"))

    if payment_form.capacity != -1:
        pending_payments = successful_payments + transactions.filter(
            is_payed=None,
            creation_time__gt=timezone.now() - datetime.timedelta(minutes=10)).count()
        if pending_payments >= payment_form.capacity:
            return {"status": "at_full_capacity", "content": content}

    if plan.is_full:
        return {"status": "at_full_capacity", "content": content}

    transaction = transaction_class.new_payment_transaction(request, payment_form, plan,
                                                            request_uuid)

    if transaction is None:
        return {"status": "gateway_error", "content": content}

    return {"status": "payment", "payment_url": transaction.get_payment_url(), "content": content}


def from_bank(request, transaction_type, transaction_id):
    transaction_class = get_transaction_class(transaction_type)
    transaction = transaction_class.objects.get(id=transaction_id)
    ret = transaction.from_bank(request)
    return ret or render(request, 'pages/error.html',
                         {"page": transaction.price_group.payment_form,
                          "title": _("UnSuccessful Payment Transaction")})
