from modeltranslation.translator import translator, TranslationOptions

from .models import PaymentFormPage, PriceGroup, PaymentGateway


class TranslatedPaymentGateway(TranslationOptions):
    fields = ("title",)


translator.register(PaymentGateway, TranslatedPaymentGateway)


class TranslatedPaymentFormPage(TranslationOptions):
    fields = ("payment_description", "content")


translator.register(PaymentFormPage, TranslatedPaymentFormPage)


class TranslatedPriceGroupPage(TranslationOptions):
    fields = ("group_identifier",)


translator.register(PriceGroup, TranslatedPriceGroupPage)
