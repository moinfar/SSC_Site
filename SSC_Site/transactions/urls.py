from django.conf.urls import url

from transactions.views import check_discount_code

urlpatterns = [
    url(r'^check-discount-code/$', check_discount_code, name='check_discount_code'),
]
