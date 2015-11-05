from copy import deepcopy
from django.contrib import admin
from mezzanine.core import admin as mezzanineAdmin
from mezzanine.blog.models import BlogPost
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.pages.admin import PageAdmin
from .models import GroupsInfoPage, GroupInfo, GroupMember


blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)
blog_fieldsets[0][1]["fields"].insert(+1, "page")
blog_fieldsets[0][1]["fields"].insert(-1, "read_more_text")


class MyBlogPostAdmin(BlogPostAdmin):
    fieldsets = blog_fieldsets


admin.site.unregister(BlogPost)
admin.site.register(BlogPost, MyBlogPostAdmin)


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