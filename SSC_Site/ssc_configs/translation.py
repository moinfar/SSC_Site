from modeltranslation.translator import translator, TranslationOptions
from .models import GroupsInfoPage, GroupInfo, GroupMember
from mezzanine.blog.translation import TranslatedBlogPost
from mezzanine.blog.models import BlogPost


class TranslatedGroupsInfoPage(TranslationOptions):
    fields = ()


class TranslatedGroupInfo(TranslationOptions):
    fields = ('title',)


class TranslatedGroupMember(TranslationOptions):
    fields = ('name', 'duty',)


translator.register(GroupsInfoPage, TranslatedGroupsInfoPage)
translator.register(GroupInfo, TranslatedGroupInfo)
translator.register(GroupMember, TranslatedGroupMember)


# class TranslatedInjectedPage(TranslatedBlogPost):
#     field = ('read_more_text',),
#
# translator.unregister(BlogPost)
# translator.register(BlogPost, TranslatedInjectedPage)