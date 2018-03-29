import re
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.models import Orderable
from mezzanine.pages.models import Page
from mezzanine.utils.email import send_mail_template


class Announcement(models.Model):
    subject = models.CharField(max_length=1000, verbose_name=_("subject"), )
    recipients = models.TextField(verbose_name=_("recipients"),
                                  help_text=_("enter recipients' emails "
                                              "separated by comma, enter or space"))
    message = models.TextField(verbose_name=_('message'))

    def clean(self):
        super().clean()
        self.recipient_list = [recipient for recipient in re.split(',| |\n|\r', self.recipients) if recipient]
        invalid_addresses = []
        print(self.recipients)
        for recipient in self.recipient_list:
            print(recipient, len(recipient))
            try:
                validate_email(recipient)
            except ValidationError:
                invalid_addresses.append(recipient)

        if invalid_addresses:
            raise ValidationError({'recipients': 'Invalid email addresses: ' + ", ".join(invalid_addresses)})

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.pk is None:
            send_mail(subject=self.subject,
                      from_email=settings.DEFAULT_FROM_EMAIL,
                      message="", html_message=self.message, recipient_list=self.recipient_list)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")


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
