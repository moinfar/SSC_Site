import datetime
import uuid
from itertools import chain

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _
from mezzanine.forms.page_processors import form_processor
from mezzanine.pages.page_processors import processor_for

from ssc_template.templatetags.other_ssc_tags import is_captcha, field_value
from transactions.payment_transaction import UpalPaymentTransaction, ZpalPaymentTransaction, \
    get_transaction_class
from .models import PaymentForm, PriceGroup


@processor_for(PaymentForm)
def payment_form_processor(request, page):
    payment_form = page.form.paymentform
    content = payment_form.content
    payment_form.send_email = False

    transaction_class = get_transaction_class(payment_form.payment_gateway.type)
    transactions = transaction_class.objects.filter(price_group__payment_form=page).order_by("-id")

    if payment_form.capacity != -1:
        successful_payment_count = transactions.filter(Q(is_paid=True) | Q(is_paid=None,
                                                                           creation_time__gt=timezone.now() - datetime.timedelta(
                                                                               minutes=10))).count()

    if payment_form.fields.filter(label="UUID").count() != 1:
        return {"status": "design_error", "content": content}

    uuid_key = "field_{}".format(payment_form.fields.get(label="UUID").id)
    if request.POST:
        mutable = request.POST._mutable
        request.POST._mutable = True
        request_uuid = uuid.uuid4()
        request.POST[uuid_key] = request_uuid
        request.POST._mutable = mutable

    form = form_processor(request, payment_form, response_redirect=False)

    if isinstance(form, dict) and "form" in form and payment_form.form.is_valid == False:
        if request.user.has_perm('transactions.can_view_payment_transactions'):
            form_fields = payment_form.fields.all().order_by("id")
            form_fields = [field for field in form_fields if not is_captcha(field)]
            form_field_labels = [field.label for field in form_fields]

            headers = [_("Creation Time"), _("Price Group"), _("Discount Code"), _("Paid Amount in Tomans"),
                       _("Is Paid"), _("Payment Time")]
            if transaction_class == UpalPaymentTransaction:
                headers.append(_("Bank Token"))
            elif transaction_class == ZpalPaymentTransaction:
                headers.append(_("Reference ID"))
            for title in headers:
                form_field_labels.append(title)
            successful_transactions = transactions.filter(is_paid=True)
            pending_transactions = transactions.filter(is_paid=None)
            failed_transactions = transactions.filter(is_paid=False)
            transactions = chain(successful_transactions, pending_transactions,
                                 failed_transactions)
            transactions_info = []
            for transaction in transactions:
                entries = transaction.get_transaction_entries()
                if entries is not None:
                    entries = [field_value(entries, field) for field in form_fields]

                    values = [
                        transaction.creation_time,
                        transaction.price_group.group_identifier + " (" + str(
                            transaction.price_group.payment_amount) + ")",
                        transaction.discount_code,
                        transaction.payment_amount,
                        transaction.is_paid,
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
                    "form_fields": form_field_labels, "transactions_info": transactions_info,
                    "content": content}

        if payment_form.capacity != -1:
            if successful_payment_count >= payment_form.capacity:
                return {"status": "at_full_capacity", "content": content, "successful_payment_count":successful_payment_count}

        return {"status": "form", "form": form["form"], "payment_form": payment_form,
                "content": content, "successful_payment_count":successful_payment_count}

    plan = PriceGroup.objects.get(id=request.POST.get("payment_plan_id"))

    if payment_form.capacity != -1:
        if successful_payment_count >= payment_form.capacity:
            return {"status": "at_full_capacity", "content": content}

    if plan.is_full:
        return {"status": "at_full_capacity", "content": content}

    discount_code = request.POST.get('discount_code')
    payment_amount = None
    if discount_code:
        result = plan.validate_discount_code(discount_code)
        if 'error' in result:
            return {"status": "form", "form": form["form"], "payment_form": payment_form,
                    "content": content, "discount_code": discount_code,
                    "discount_code_error": result['error']}
        payment_amount = result['new_price']
    else:
        discount_code = None

    transaction = transaction_class.new_payment_transaction(request, payment_form, plan,
                                                            discount_code, payment_amount,
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
