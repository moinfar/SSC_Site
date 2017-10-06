from modeltranslation.translator import translator, TranslationOptions

from .models import GalleryContainerPage
from .models import GroupsInfoPage, GroupInfo, GroupMember, Person, Duty


class TranslatedPerson(TranslationOptions):
    fields = ("name",)


class TranslatedDuty(TranslationOptions):
    fields = ("title",)


class TranslatedGroupsInfoPage(TranslationOptions):
    fields = ()


class TranslatedGroupInfo(TranslationOptions):
    fields = ('title',)


class TranslatedGroupMember(TranslationOptions):
    fields = ()


translator.register(Person, TranslatedPerson)
translator.register(Duty, TranslatedDuty)
translator.register(GroupsInfoPage, TranslatedGroupsInfoPage)
translator.register(GroupInfo, TranslatedGroupInfo)
translator.register(GroupMember, TranslatedGroupMember)


# class TranslatedInjectedPage(TranslatedBlogPost):
#     field = ('read_more_text',),
#
# translator.unregister(BlogPost)
# translator.register(BlogPost, TranslatedInjectedPage)


class TranslatedGalleryContainerPage(TranslationOptions):
    fields = ()


translator.register(GalleryContainerPage, TranslatedGalleryContainerPage)
