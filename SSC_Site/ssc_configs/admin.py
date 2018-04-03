import html

import os
from copy import deepcopy
from django.contrib import admin
from django.core.mail import send_mail, get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from django.utils import translation
from django.utils.html import format_html
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.blog.models import BlogPost
from mezzanine.core import admin as mezzanineAdmin
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin

from ssc_configs.models import Announcement, Attachment
from .models import GalleryContainerPage
from .models import GroupsInfoPage, GroupInfo, GroupMember, Person, Duty

blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)
blog_fieldsets[0][1]["fields"].insert(+1, "page")
blog_fieldsets[0][1]["fields"].insert(-1, "read_more_text")


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'subject']

    def add_view(self, *args, **kwargs):
        self.readonly_fields = []
        self.exclude = []
        self.inlines = [AttachmentInline]
        return super().add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.readonly_fields = ['id', 'from_email', 'subject', 'language', 'date', 'message_safe',
                                'attachments', 'recipients']
        self.inlines = []
        self.exclude = ['message']
        return super().change_view(*args, **kwargs)

    def attachments(self, obj):
        return format_html('<br>'.join([str(attachment) for attachment in obj.attachments.all()]))

    def message_safe(self, obj):
        return format_html(html.unescape(obj.message))
    message_safe.short_description = 'message'

    def save_model(self, request, obj, form, change):
        context = {'message': obj.message, 'request': request, 'site_url': settings.SITE_URL}
        if obj.pk is None:
            former_language = translation.get_language()
            translation.activate(obj.language)
            message = get_template('email/announcement.html').render(context=context)
            email = EmailMultiAlternatives(subject=obj.subject,
                                           from_email=obj.from_email,
                                           body=message, to=obj.recipient_list)
            email.content_subtype = 'html'
            self.announcement = obj
            self.email = email  # Email will be sent when attachments are saved and accessible
            translation.activate(former_language)
        return super().save_model(request, obj, form, change)

    def save_related(self, *args, **kwargs):
        ret = super().save_related(*args, **kwargs)
        if hasattr(self, 'announcement'):
            for attachment in self.announcement.attachments.all():
                file = attachment.file
                self.email.attach(file.name, file.read())
            self.email.send()
        return ret

admin.site.register(Announcement, AnnouncementAdmin)


class MyBlogPostAdmin(BlogPostAdmin):
    fieldsets = blog_fieldsets


admin.site.unregister(BlogPost)
admin.site.register(BlogPost, MyBlogPostAdmin)


class PersonAdmin(mezzanineAdmin.BaseTranslationModelAdmin):
    fieldsets = ((None, {"fields": ("slug", "name")}),)
    list_display = ("slug", "name")
    list_display_links = ("slug", "name")
    list_filter = ("slug", "name")
    search_fields = ("slug", "name")


admin.site.register(Person, PersonAdmin)


class DutyAdmin(mezzanineAdmin.BaseTranslationModelAdmin):
    fieldsets = ((None, {"fields": ("slug", "title")}),)
    list_display = ("slug", "title")
    list_display_links = ("slug", "title")
    list_filter = ("slug", "title")
    search_fields = ("slug", "title")


admin.site.register(Duty, DutyAdmin)


class GroupInfoInline(mezzanineAdmin.TabularDynamicInlineAdmin):
    model = GroupInfo


class GroupsInfoPageAdmin(PageAdmin):
    inlines = (GroupInfoInline,)
    fieldsets = deepcopy(PageAdmin.fieldsets)


admin.site.register(GroupsInfoPage, GroupsInfoPageAdmin)


class GroupMemberInline(mezzanineAdmin.TabularDynamicInlineAdmin):
    model = GroupMember


class GroupInfoAdmin(mezzanineAdmin.BaseTranslationModelAdmin):
    fieldsets = ((None, {"fields": ("page", "title",)}),)
    inlines = (GroupMemberInline,)
    list_display = ("page", "title",)
    list_display_links = ("title",)
    list_editable = ("page",)
    list_filter = ("page", "title",)
    search_fields = ("page", "title",)


admin.site.register(GroupInfo, GroupInfoAdmin)


class GalleryContainerPageAdmin(PageAdmin):
    fieldsets = deepcopy(PageAdmin.fieldsets)


admin.site.register(GalleryContainerPage, GalleryContainerPageAdmin)
