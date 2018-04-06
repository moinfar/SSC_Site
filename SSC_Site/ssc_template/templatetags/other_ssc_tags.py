import datetime

from django.core.exceptions import ObjectDoesNotExist
from mezzanine.forms import fields as mezzanine_fields
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.utils import timezone
from mezzanine import template

from screens.models import ScreenPage
from .jdate_tags import farsi_digits

register = template.Library()


@register.filter()
def is_radio_select(instance):
    return type(instance) == RadioSelect


@register.filter()
def is_multiple_checkbox(instance):
    return type(instance) == CheckboxSelectMultiple


@register.filter()
def get_post_real_url(post):
    if post.page is not None:
        return post.page.get_absolute_url
    return post.get_absolute_url


@register.filter()
def post_is_new(post):
    return post.publish_date > timezone.now() - datetime.timedelta(days=7)


@register.filter()
def get_persian_comma_separated_money(number):
    return farsi_digits(format(number, ','))


@register.filter()
def has_expired(expirable_model):
    return expirable_model.expiry_date and expirable_model.expiry_date < timezone.now()


@register.filter()
def has_published(publishable_model):
    return publishable_model.publish_date < timezone.now()


@register.as_tag
def get_screenpage(screen_lable):
    return ScreenPage.objects.get(label=screen_lable)


@register.filter()
def is_captcha(field):
    return field.field_type == mezzanine_fields.CAPTCHA


@register.filter()
def at_index(list, index):
    return list[index]


@register.filter()
def admin_edit_link(page):
    content_model = page.get_content_model()
    return '/en/admin/{app_label}/{model_name}/{pk}/change'.format(
        app_label=content_model._meta.app_label,
        model_name=content_model.__class__.__name__.lower(),
        pk=content_model.pk
    )


@register.filter()
def field_value(entries, field):
    try:
        return entries.get(field_id=field.id).value
    except ObjectDoesNotExist:
        return '----'
