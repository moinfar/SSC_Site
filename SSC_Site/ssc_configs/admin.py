import html

import os
from copy import deepcopy
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from django.utils import translation
from django.utils.html import format_html, strip_tags
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.blog.models import BlogPost
from mezzanine.core import admin as mezzanineAdmin
from mezzanine.pages.admin import PageAdmin

from ssc_configs.models import Announcement, Attachment, MailingList, EmailListTextField
from .models import GalleryContainerPage
from .models import GroupsInfoPage, GroupInfo, GroupMember, Person, Duty

blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)
blog_fieldsets[0][1]["fields"].insert(+1, "page")
blog_fieldsets[0][1]["fields"].insert(-1, "read_more_text")


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'

    def clean(self):
        super().clean()
        if self.instance.pk:
            return
        all_recipients = EmailListTextField.to_list(self.cleaned_data['recipients']) + [
            mailing_list.get_emails_list() for mailing_list in self.cleaned_data['recipients_mailing_lists']
        ]
        if not all_recipients:
            raise ValidationError('Recipients email address cannot be empty. Please enter '
                                  'at least one valid email address or select mailing lists '
                                  'with valid emails')
        self.cleaned_data['all_recipients'] = all_recipients

        self.cleaned_data['all_cc'] = EmailListTextField.to_list(self.cleaned_data['cc']) + [
            mailing_list.get_emails_list() for mailing_list in self.cleaned_data['cc_mailing_lists']
        ]
        self.cleaned_data['all_bcc'] = EmailListTextField.to_list(self.cleaned_data['bcc']) + [
            mailing_list.get_emails_list() for mailing_list in self.cleaned_data['bcc_mailing_lists']
        ]


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'subject', 'message_preview']
    list_display_links = ['id', 'subject', 'message_preview']
    search_fields = ['subject', 'message']
    filter_horizontal = ['recipients_mailing_lists', 'cc_mailing_lists', 'bcc_mailing_lists']
    form = AnnouncementForm

    fieldsets = [('', {'fields': ['from_email', 'subject', 'message', 'language']}),
                 ('recipients', {'fields': ['recipients', 'recipients_mailing_lists'],
                                 'description': 'Enter email addresses directly or choose one '
                                                'or more mailing list'}),
                 ('cc', {'fields': ['cc', 'cc_mailing_lists'], 'classes': ['collapse', 'collapse-closed']}),
                 ('bcc', {'fields': ['bcc', 'bcc_mailing_lists'], 'classes': ['collapse', 'collapse-closed']}),
                 ]

    def add_view(self, *args, **kwargs):
        self.readonly_fields = []
        self.exclude = []
        self.inlines = [AttachmentInline]
        return super().add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.readonly_fields = ['id', 'from_email', 'subject', 'language', 'date', 'message_safe',
                                'attachments', 'recipients', 'recipients_mailing_lists']
        self.inlines = []
        self.exclude = ['message']
        return super().change_view(*args, **kwargs)

    def attachments(self, obj):
        return format_html('<br>'.join([str(attachment) for attachment in obj.attachments.all()]))

    def message_preview(self, obj):
        return strip_tags(html.unescape(obj.message))[:20]

    def message_safe(self, obj):
        return format_html(html.unescape(obj.message))
    message_safe.short_description = 'message'

    def save_model(self, request, obj, form, change):
        if obj.pk is None:
            context = {'message': obj.message, 'request': request, 'site_url': settings.SITE_URL}
            former_language = translation.get_language()
            translation.activate(obj.language)
            message = get_template('email/announcement.html').render(context=context)
            email = EmailMultiAlternatives(subject=obj.subject,
                                           from_email=obj.from_email,
                                           body=message, to=form.cleaned_data['all_recipients'],
                                           cc=form.cleaned_data['all_cc'],
                                           bcc=form.cleaned_data['all_bcc'])
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
            #self.email.send()
        return ret

admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(MailingList)

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
