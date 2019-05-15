import json
import logging
import uuid
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, build_opener
from django.conf import settings

from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class BibotWidget(widgets.Widget):
    template_name = "mezzacaptcha/bibot.html"

    def __init__(self, api_params=None, *args, **kwargs):
        super(BibotWidget, self).__init__(*args, **kwargs)
        self.uuid = uuid.uuid4().hex
        self.api_params = api_params or {}

    def value_from_datadict(self, data, files, name):
        return data.get("bibot-response", None)

    def get_context(self, name, value, attrs):
        context = super(BibotWidget, self).get_context(name, value, attrs)
        params = urlencode(self.api_params)
        context.update({
            "public_key": self.attrs["data-sitekey"],
            "widget_uuid": self.uuid,
            "api_params": params,
        })
        return context

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super(BibotWidget, self).build_attrs(base_attrs, extra_attrs)
        attrs["data-widget-uuid"] = self.uuid
        return attrs


class BibotResponse(object):
    def __init__(self, is_valid, error_codes=None):
        self.is_valid = is_valid
        self.error_codes = error_codes or []


def submit(bibot_response, private_key):
    response = build_opener().open(Request(
        url="https://api.bibot.ir/api1/siteverify/",
        data=urlencode({
            "secret": private_key,
            "response": bibot_response,
        }).encode("utf-8"),
        headers={
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "bibot Django"
        }
    ))
    data = json.loads(response.read().decode("utf-8"))
    response.close()
    return BibotResponse(is_valid=data["success"], error_codes=data.get("error-codes"))


class BibotField(forms.CharField):
    widget = BibotWidget
    default_error_messages = {
        "captcha_invalid": _("Error verifying bibot, please try again."),
        "captcha_error": _("Error verifying bibot, please try again."),
    }

    def __init__(self, public_key=None, private_key=None, *args, **kwargs):
        super(BibotField, self).__init__(*args, **kwargs)
        self.required = True
        self.private_key = private_key or settings.BIBOT_PRIVATE_KEY
        self.public_key = public_key or settings.BIBOT_PUBLIC_KEY

        self.widget.attrs["data-sitekey"] = self.public_key

    def validate(self, value):
        super(BibotField, self).validate(value)

        try:
            check_captcha = submit(bibot_response=value, private_key=self.private_key)

        except HTTPError:
            raise ValidationError(self.error_messages["captcha_error"], code="captcha_error")

        if not check_captcha.is_valid:
            logger.error("bibot validation failed due to: %s" % check_captcha.error_codes)
            raise ValidationError(self.error_messages["captcha_invalid"], code="captcha_invalid")
