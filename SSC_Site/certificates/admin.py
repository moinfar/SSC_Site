from django.contrib import admin

# Register your models here.
from certificates.models import Certificate
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

class CertificateAdmin(admin.ModelAdmin):
    fields = ('name', 'data', 'template')
    list_display = ('name', 'data', 'template', 'download_certificates')

    def download_certificates(self, obj):
        return '<a href="%s">%s</a>' % (reverse('download_certificate', args=(obj.id,)), _("Download"))
    download_certificates.short_description = 'Download'
    download_certificates.allow_tags = True

admin.site.register(Certificate, CertificateAdmin)
