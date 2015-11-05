from modeltranslation.translator import translator, TranslationOptions
from mezzanine.blog.translation import TranslatedBlogPost
from mezzanine.blog.models import BlogPost


# class TranslatedInjectedPage(TranslatedBlogPost):
#     field = ('read_more_text',),
#
# translator.unregister(BlogPost)
# translator.register(BlogPost, TranslatedInjectedPage)