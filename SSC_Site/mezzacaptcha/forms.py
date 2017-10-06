from captcha.fields import ReCaptchaField
from mezzanine.generic.forms import ThreadedCommentForm
from django.utils.translation import ugettext_lazy as _


class CaptchaThreadedCommentForm(ThreadedCommentForm):
    """ Adds a reCaptcha field to the comment form in blog
    """
    captcha = ReCaptchaField(label=_('Captcha'))
