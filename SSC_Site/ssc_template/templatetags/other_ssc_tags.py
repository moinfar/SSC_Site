from django import template
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
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
