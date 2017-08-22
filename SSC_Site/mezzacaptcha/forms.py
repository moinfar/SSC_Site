from django import forms
from captcha.fields import CaptchaField
from mezzanine.generic.forms import ThreadedCommentForm
from django.utils.translation import ugettext_lazy as _


class CaptchaThreadedCommentForm(ThreadedCommentForm):
    """ Adds a captcha field to the comment form in blog
    """
    captcha = CaptchaField(label=_("Please enter the captcha"))
