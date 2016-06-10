from modeltranslation.translator import translator, TranslationOptions
from .models import VideoContainerPage, VideoFrame, Video


class TranslatedVideoContainerPage(TranslationOptions):
    fields = ()


class TranslatedVideo(TranslationOptions):
    fields = ("title", "description")


class TranslatedVideoFrame(TranslationOptions):
        fields = ()


translator.register(VideoContainerPage, TranslatedVideoContainerPage)
translator.register(Video, TranslatedVideo)
translator.register(VideoFrame, TranslatedVideoFrame)
