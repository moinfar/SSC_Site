from modeltranslation.translator import translator, TranslationOptions

from .models import ScreenPage, ScreenImage


class TranslatedScreenPage(TranslationOptions):
    fields = ("content",)


class TranslatedScreenImage(TranslationOptions):
    fields = ("content",)


translator.register(ScreenPage, TranslatedScreenPage)
translator.register(ScreenImage, TranslatedScreenImage)
