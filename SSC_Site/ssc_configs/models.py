from django.db import models
from mezzanine.pages.models import Page
from mezzanine.core.models import Orderable
from django.utils.translation import ugettext_lazy as _


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
    name = models.CharField(max_length=500, blank=False, null=False, verbose_name=_("Full Name"))
    duty = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("Duty"))

    class Meta:
        verbose_name = _("Group Member")
        verbose_name_plural = _("Group Members")