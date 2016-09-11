from django.contrib import admin
from mezzanine.conf import settings

# Register your models here.
from django.core import urlresolvers
from certificates.models import Certificate
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

class CertificateAdmin(admin.ModelAdmin):
    fields = ('name', 'data', 'template')
    list_display = ('name', 'data', 'template', 'compile_certificate', 'get_pdf_output', 'get_compile_process')

    def compile_certificate(self, obj):
        if obj.compile_process.status == 'R':
            return '%s' % (_("Compiling"),)
        else:
            return '<a href="%s">%s</a>' % (reverse('compile_certificate', args=(obj.id,)), _("Compile"))
    compile_certificate.short_description = 'Compile'
    compile_certificate.allow_tags = True

    def get_compile_process(self, obj):
        if obj.compile_process:
            link = urlresolvers.reverse("admin:subprocess_manager_subprocess_change", args=[obj.compile_process.id])
            return u'<a href="%s">%s</a>' % (link, obj.compile_process.status)
        else:
            return u''
    get_compile_process.short_description = 'Compile Status'
    get_compile_process.allow_tags = True

    def get_pdf_output(self, obj):
        filename = 'certificates/out/cert_%d.pdf' % obj.id
        return u'<a href="%s">%s</a>' % (settings.MEDIA_URL + filename, _("Download"))
    get_pdf_output.short_description = 'PDF Output'
    get_pdf_output.allow_tags = True

admin.site.register(Certificate, CertificateAdmin)
