from django.db import models
from mezzanine.core.fields import FileField
from django.utils.translation import ugettext_lazy as _

from subprocess_manager.models import Subprocess


class Certificate(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=50)
    data = FileField(verbose_name=_("Data (CSV)"), max_length=500, extensions=('.csv',),
                     upload_to='certificates/data_files')
    template = FileField(verbose_name=_("Template (Zip)"), max_length=500, extensions=('.zip',),
                         upload_to='certificates/templates')
    compile_process = models.ForeignKey('subprocess_manager.Subprocess',
                                        verbose_name=_("Compile process"), null=True,
                                        editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.compile_process = Subprocess.objects.create()
            super(Certificate, self).save()

    def delete(self, using=None):
        if self.compiler:
            self.compiler.delete()

    class Meta:
        permissions = (
            ('can_compile', 'User can compile the certificate'),
        )
