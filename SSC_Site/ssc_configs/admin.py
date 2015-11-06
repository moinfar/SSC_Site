from copy import deepcopy
from django.contrib import admin
from mezzanine.core import admin as mezzanineAdmin
from mezzanine.blog.models import BlogPost
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.pages.admin import PageAdmin
from .models import GroupsInfoPage, GroupInfo, GroupMember, Person, Duty
from .models import GalleryContainerPage


blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)
blog_fieldsets[0][1]["fields"].insert(+1, "page")
blog_fieldsets[0][1]["fields"].insert(-1, "read_more_text")


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
    inlines = (GroupMemberInline, )
    list_display = ("page", "title",)
    list_display_links = ("title",)
    list_editable = ("page",)
    list_filter = ("page", "title",)
    search_fields = ("page", "title",)

admin.site.register(GroupInfo, GroupInfoAdmin)


class GalleryContainerPageAdmin(PageAdmin):
    fieldsets = deepcopy(PageAdmin.fieldsets)

admin.site.register(GalleryContainerPage, GalleryContainerPageAdmin)