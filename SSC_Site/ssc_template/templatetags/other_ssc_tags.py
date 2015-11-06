import locale
from django import template
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
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
def get_persian_comma_separated_money(number):
    return farsi_digits(format(number, ','))