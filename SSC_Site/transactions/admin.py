from copy import deepcopy
from django.contrib import admin
from mezzanine.core import admin as mezzanineAdmin
from mezzanine.forms.admin import FormAdmin, FieldAdmin
from mezzanine.pages.admin import PageAdmin

from .models import PaymentForm, PriceGroup, PaymentGateway, DiscountCode


class PaymentGatewayAdmin(mezzanineAdmin.BaseTranslationModelAdmin):
    fieldsets = ((None, {"fields": ("title", "type", "gateway_id", "gateway_api")}),)
    list_display = ("type", "title", "gateway_id", "gateway_api")
    list_display_links = ("title", "gateway_id", "gateway_api")
    list_filter = ("type", "title", "gateway_id", "gateway_api")
    search_fields = ("type", "title")


admin.site.register(PaymentGateway, PaymentGatewayAdmin)

form_fieldsets = deepcopy(FormAdmin.fieldsets)
form_fieldsets[0][1]["fields"].insert(+3, "payment_gateway")
form_fieldsets[0][1]["fields"].insert(+4, "payment_description")
form_fieldsets[0][1]["fields"].insert(+5, "capacity")


class DiscountCodeInline(mezzanineAdmin.TabularDynamicInlineAdmin):
    model = DiscountCode


class PriceGroupInline(mezzanineAdmin.TabularDynamicInlineAdmin):
    model = PriceGroup
    inlines = [DiscountCodeInline]


class PaymentFormAdmin(FormAdmin):
    inlines = [FieldAdmin, PriceGroupInline]
    fieldsets = form_fieldsets


admin.site.register(PaymentForm, PaymentFormAdmin)
