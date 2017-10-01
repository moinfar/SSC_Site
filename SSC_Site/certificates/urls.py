from django.conf.urls import url

from certificates.views import compile_certificate

urlpatterns = [
    url(r'^compile/(?P<cid>\d+)$', compile_certificate, name='compile_certificate'),
]
