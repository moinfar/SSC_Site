from copy import deepcopy
from django.contrib import admin
from mezzanine.core import admin as mezzanineAdmin
from mezzanine.pages.admin import PageAdmin

from .models import ScreenPage, ScreenImage

screen_page_fieldsets = deepcopy(PageAdmin.fieldsets)
screen_page_fieldsets[0][1]["fields"].insert(+1, "label")
screen_page_fieldsets[0][1]["fields"].insert(+4, "content")


class ScreenPageAdmin(PageAdmin):
    fieldsets = screen_page_fieldsets


admin.site.register(ScreenPage, ScreenPageAdmin)


class ScreenImageAdmin(mezzanineAdmin.BaseTranslationModelAdmin):
    fieldsets = ((None, {
        "fields": ("screen", "publish_date", "expiry_date", "image", "content", "is_default")}),)
    list_display = ("admin_thumb", "screen", "publish_date", "expiry_date")
    list_display_links = ("admin_thumb", "screen", "publish_date")
    list_editable = ("expiry_date",)
    list_filter = ("screen", "publish_date", "expiry_date")
    search_fields = ("screen", "content")


admin.site.register(ScreenImage, ScreenImageAdmin)
