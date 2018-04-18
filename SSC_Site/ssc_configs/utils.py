import re
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import ugettext as _
from django.db import models


class EmailListFormField(forms.CharField):
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['rows'] = '1'
        return attrs


class EmailListTextField(models.TextField):
    @staticmethod
    def to_list(value):
        return [email_address for email_address in re.split(',| |\n|\r', value or '') if
                email_address]

    def formfield(self, **kwargs):
        help_text = _("enter email addresses separated by comma, enter or space")
        kwargs.update({'form_class': EmailListFormField, 'help_text': help_text})
        return super().formfield(**kwargs)

    def validate(self, value, model_instance):
        invalid_addresses = []
        list = self.to_list(value)
        if not list and not self.null:
            raise ValidationError('Please enter at least one email address')
        for email in list:
            try:
                validate_email(email)
            except ValidationError:
                invalid_addresses.append(email)

        if invalid_addresses:
            raise ValidationError('Invalid email addresses: ' + ", ".join(invalid_addresses))
