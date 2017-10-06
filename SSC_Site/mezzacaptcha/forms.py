from mezzanine.generic.forms import ThreadedCommentForm
from captcha.fields import ReCaptchaField


class CaptchaThreadedCommentForm(ThreadedCommentForm):
    """ Adds a reCaptcha field to the comment form in blog
    """
    captcha = ReCaptchaField()
