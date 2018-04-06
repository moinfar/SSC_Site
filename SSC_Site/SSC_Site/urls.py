from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.i18n import set_language
from mezzanine.conf import settings
from mezzanine.core.views import direct_to_template
from shortener import urls as shortener_urls

from certificates import urls as certificate_urls
from transactions import urls as transaction_urls
from transactions.page_processors import from_bank

admin.autodiscover()

# Add the urlpatterns for any custom Django applications here.
# You can also change the ``home`` view to add your own functionality
# to the project's homepage.

urlpatterns = i18n_patterns(
    url("^admin/", include(admin.site.urls)),
)

if settings.USE_MODELTRANSLATION:
    urlpatterns += [
        url('^i18n/$', set_language, name='set_language'),
    ]

urlpatterns += [
    url('^$', direct_to_template, {'template': 'index.html'}, name='home'),
    url('^from_bank/(?P<transaction_type>\w+)/(?P<transaction_id>\d+)/$', from_bank,
        name='transactions_from_bank'),
    url('^go/', include(shortener_urls)),
    url('^cert/', include(certificate_urls)),
    url('^transactions/', include(transaction_urls)),
    url('^', include('mezzanine.urls')),
]

# Adds ``STATIC_URL`` to the context of error pages, so that error
# pages can use JS, CSS and images.
handler404 = "mezzanine.core.views.page_not_found"
handler500 = "mezzanine.core.views.server_error"
