from django.conf.urls import patterns, url

urlpatterns = patterns('certificates.views',
    url(r'^download/(?P<cid>\d+)$', 'download_certificate', name='download_certificate'),
)
