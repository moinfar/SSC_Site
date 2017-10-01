# -*- coding: utf-8 -*-


import celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SSC_Site.settings')

from django.conf import settings

app = celery.Celery('SSC_Site')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
