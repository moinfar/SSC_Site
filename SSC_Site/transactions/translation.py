from modeltranslation.translator import translator, TranslationOptions

from .models import PaymentForm, PriceGroup, PaymentGateway


class TranslatedPaymentGateway(TranslationOptions):
    fields = ("title",)


translator.register(PaymentGateway, TranslatedPaymentGateway)


class TranslatedPaymentForm(TranslationOptions):
    fields = ("payment_description",) 


translator.register(PaymentForm, TranslatedPaymentForm)


class TranslatedPriceGroup(TranslationOptions):
    fields = ("group_identifier",)


translator.register(PriceGroup, TranslatedPriceGroup)
