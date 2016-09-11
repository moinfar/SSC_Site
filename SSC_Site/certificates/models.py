from django.db import models
from mezzanine.core.fields import FileField
from django.utils.translation import ugettext_lazy as _


class Certificate(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=50)
    data = FileField(verbose_name=_("Data (CSV)"), max_length=500, extensions=('.csv',),
                     upload_to='certificates/data_files')
    template = FileField(verbose_name=_("Template (Zip)"), max_length=500, extensions=('.zip',),
                         upload_to='certificates/templates')

    class Meta:
        permissions = (
            ('can_download', 'User can download the certificate'),
        )
