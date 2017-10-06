from django.db import models
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.models import Orderable
from mezzanine.pages.models import Page


class Person(models.Model):
    slug = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("slug"),
                            unique=True)
    name = models.CharField(max_length=500, blank=False, null=False, verbose_name=_("Name"))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")


class Duty(models.Model):
    slug = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("slug"),
                            unique=True)
    title = models.CharField(max_length=500, blank=False, null=False, verbose_name=_("Title"))

    def __unicode__(self):
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
