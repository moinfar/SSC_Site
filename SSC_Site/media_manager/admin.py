from copy import deepcopy
from django.contrib import admin
from mezzanine.core import admin as mezzanineAdmin
from mezzanine.pages.admin import PageAdmin

from .models import VideoContainerPage, VideoFrame, Video


class VideoInline(mezzanineAdmin.StackedDynamicInlineAdmin):
    model = Video


class VideoContainerPageAdmin(PageAdmin):
    inlines = (VideoInline,)
    fieldsets = deepcopy(PageAdmin.fieldsets)

admin.site.register(VideoContainerPage, VideoContainerPageAdmin)


class VideoFrameInline(mezzanineAdmin.TabularDynamicInlineAdmin):
    model = VideoFrame


class VideoAdmin(mezzanineAdmin.BaseTranslationModelAdmin):
    fieldsets = ((None, {"fields": ("page", "title", "description", )}),)
    inlines = (VideoFrameInline, )
    list_display = ("page", "title")
    list_display_links = ("title",)
    list_editable = ("page",)
    list_filter = ("page", "title",)
    search_fields = ("page", "title", "description")

admin.site.register(Video, VideoAdmin)




