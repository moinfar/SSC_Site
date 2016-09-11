from django.conf.urls import patterns, url

urlpatterns = patterns('certificates.views',
    url(r'^compile/(?P<cid>\d+)$', 'compile_certificate', name='compile_certificate'),
)
