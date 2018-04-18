from django import forms
from django.core.exceptions import ValidationError

from ssc_configs.models import Announcement
from ssc_configs.utils import EmailListTextField


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'

    def clean(self):
        super().clean()
        if self.instance.pk:
            return
        all_recipients = EmailListTextField.to_list(self.cleaned_data['recipients']) + [
            email for mailing_list in self.cleaned_data['recipients_mailing_lists'] for email in mailing_list.get_emails_list()
        ]
        self.cleaned_data['all_recipients'] = all_recipients

        self.cleaned_data['all_cc'] = EmailListTextField.to_list(self.cleaned_data['cc']) + [
            email for mailing_list in self.cleaned_data['cc_mailing_lists'] for email in mailing_list.get_emails_list()
        ]
        self.cleaned_data['all_bcc'] = EmailListTextField.to_list(self.cleaned_data['bcc']) + [
            email for mailing_list in self.cleaned_data['bcc_mailing_lists'] for email in mailing_list.get_emails_list()
        ]
