from django.db import models
from django.utils.timezone import now
from mezzanine.pages.models import Page
from mezzanine.core.models import RichText
from mezzanine.core.fields import FileField
# from mezzanine.utils.models import AdminThumbMixin
from django.utils.translation import ugettext_lazy as _


class ScreenPage(Page, RichText):
    label = models.CharField(max_length=50, null=False, blank=False, unique=True, verbose_name=_("Label"))

    def get_default_image(self):
        return self.images.filter(is_default=True).order_by('-publish_date')[:1]

    def current_images(self):
        result = self.images.filter(expiry_date__gt=now(), publish_date__lt=now()).order_by('-publish_date')
        if not result:
            return self.get_default_image()
        return result

    def recent_images(self):
        return self.images.filter(publish_date__lt=now()).order_by('-publish_date')[:15]

    def all_images(self):
        return self.images.filter(publish_date__lt=now()).order_by('-publish_date')


    class Meta:
        verbose_name = _("Screen Page")
        verbose_name_plural = _("Screen Pages")


class AdminThumbMixin(object):
    """
    Provides a thumbnail method on models for admin classes to
    reference in the ``list_display`` definition.
    """

    admin_thumb_field = None

    def admin_thumb(self):
        thumb = ""
        if self.admin_thumb_field:
            thumb = getattr(self, self.admin_thumb_field, "")
        if not thumb:
            return ""
        from mezzanine.conf import settings
        from mezzanine.core.templatetags.mezzanine_tags import thumbnail
        x, y = 160, 90
        thumb_url = thumbnail(thumb, x, y)
        return "<img src='%s%s'>" % (settings.MEDIA_URL, thumb_url)
    admin_thumb.allow_tags = True
    admin_thumb.short_description = ""


class ScreenImage(RichText, AdminThumbMixin):
    screen = models.ForeignKey(ScreenPage, related_name="images", verbose_name=_("screen"))
    image = FileField(null=True, blank=True, max_length=500, format="Image",
                      upload_to="screens/images", verbose_name=_("image"))

    publish_date = models.DateTimeField(_("Published from"),
                                        help_text=_("With Published chosen, won't be shown until this time"),
                                        blank=True, null=True, db_index=True)
    expiry_date = models.DateTimeField(_("Expires on"),
                                       help_text=_("With Published chosen, won't be shown after this time"))
    is_default = models.BooleanField(null=False, default=False, verbose_name=_("is default"))

    admin_thumb_field = "image"

    def save(self, *args, **kwargs):
        if self.publish_date is None:
            self.publish_date = now()
        super(ScreenImage, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Screen Image")
        verbose_name_plural = _("Screen Image")

