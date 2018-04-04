import re
from ckeditor.fields import RichTextField
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from mezzanine.conf import settings
from mezzanine.core.models import Orderable
from mezzanine.pages.models import Page


def get_announcement_from_emails():
    emails = settings.ANNOUNCEMENT_FROM_EMAILS if hasattr(settings,
                                                          'ANNOUNCEMENT_FROM_EMAILS') else []
    emails.append(settings.DEFAULT_FROM_EMAIL)
    return [(email, email) for email in emails]


class EmailListFormField(forms.CharField):
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['rows'] = '1'
        return attrs


class EmailListTextField(models.TextField):
    def to_list(self, value):
        return [email_address for email_address in re.split(',| |\n|\r', value or '') if
                email_address]

    def formfield(self, **kwargs):
        help_text = _("enter email addresses separated by comma, enter or space")
        kwargs.update({'form_class': EmailListFormField, 'help_text': help_text})
        return super().formfield(**kwargs)

    def validate(self, value, model_instance):
        invalid_addresses = []
        for email in self.to_list(value):
            try:
                validate_email(email)
            except ValidationError:
                invalid_addresses.append(email)

        if invalid_addresses:
            raise ValidationError('Invalid email addresses: ' + ", ".join(invalid_addresses))


class MailingList(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    email_addresses = EmailListTextField(verbose_name=_('email addresses'))

    def __str__(self):
        return self.name


class Announcement(models.Model):
    from_email = models.CharField(max_length=100, choices=get_announcement_from_emails(),
                                  verbose_name=_('from email'))
    subject = models.CharField(max_length=1000, verbose_name=_("subject"))
    recipients = EmailListTextField(verbose_name=_("recipients"))
    recipients_mailing_lists = models.ManyToManyField(to=MailingList)
    message = RichTextField(verbose_name=_('message (don\'t use table)'),
                            help_text=_("IMPORTANT WARNING: PLEASE DO NOT USE TABLE IN EMAIL! "
                                        "By the time I'm writing this, "
                                        "tables of this editor are rendered awfully"
                                        " by the mail clients. "
                                        "Make sure they are ok first by sending a test email "
                                        "containing your desired table. (Don't take account "
                                        "for the previewer of the editor)"))
    language = models.CharField(max_length=2, choices=settings.LANGUAGES,
                                default=settings.LANGUAGES[0][0], verbose_name=_('language'))
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")
        ordering = ("-date",)


@deconstructible
class SizeValidator:
    def __init__(self, max_size):  # in mega bytes
        self.max_size = max_size

    def __call__(self, obj):
        if obj.size > self.max_size * 1024 * 1024:
            raise ValidationError('File size must not be greater than {} MB'.format(self.max_size))


class Attachment(models.Model):
    announcement = models.ForeignKey(to=Announcement, related_name='attachments')
    file = models.FileField(upload_to='attachments/', validators=[SizeValidator(0.5)])

    def __str__(self):
        return format_html(
            '<a href="{url}">{name}</a>'.format(url=self.file.url, name=self.file.name))


class Person(models.Model):
    slug = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("slug"),
                            unique=True)
    name = models.CharField(max_length=500, blank=False, null=False, verbose_name=_("Name"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")


class Duty(models.Model):
    slug = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("slug"),
                            unique=True)
    title = models.CharField(max_length=500, blank=False, null=False, verbose_name=_("Title"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Duty")
        verbose_name_plural = _("Duty")


class GroupsInfoPage(Page):
    pass

    class Meta:
        verbose_name = _("Groups' Info Page")
        verbose_name_plural = _("Groups' Info Pages")


class GroupInfo(Orderable):
    page = models.ForeignKey("GroupsInfoPage", verbose_name=_("Containing Page"))
    title = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("Title"))

    class Meta:
        verbose_name = _("Group Info")
        verbose_name_plural = _("Groups Info")


class GroupMember(Orderable):
    group = models.ForeignKey("GroupInfo", verbose_name=_("Containing Group"))
    person = models.ForeignKey("Person", verbose_name=_("Person"))
    duty = models.ForeignKey("Duty", verbose_name=_("Duty"))

    class Meta:
        verbose_name = _("Group Member")
        verbose_name_plural = _("Group Members")


class GalleryContainerPage(Page):
    pass

    class Meta:
        verbose_name = _("Gallery Container Page")
        verbose_name_plural = _("Gallery Container Pages")
