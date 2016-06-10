from django.db import models
from mezzanine.pages.models import Page, RichText
from mezzanine.core.fields import RichTextField
from mezzanine.core.models import Orderable
from django.utils.translation import ugettext_lazy as _


class VideoContainerPage(Page, RichText):
    pass

    class Meta:
        verbose_name = _("Video Container Page")
        verbose_name_plural = _("Video Container Pages")


class Video(Orderable):
    page = models.ForeignKey("VideoContainerPage", verbose_name=_("Containing Page"))
    title = models.CharField(max_length=255, blank=False, null=False, verbose_name=_("Title"))
    description = RichTextField(_("Description"))

    class Meta:
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")


class VideoFrame(models.Model):
    video = models.ForeignKey("Video", verbose_name=_("Video"))
    site = models.CharField(max_length=50, blank=False, null=False, verbose_name=_("Site name"), default=_("YouTube"))
    code = models.CharField(max_length=500, blank=False, null=False, verbose_name=_("Code"))

    class Meta:
        verbose_name = _("Video Frame")
        verbose_name_plural = _("Video Frames")

