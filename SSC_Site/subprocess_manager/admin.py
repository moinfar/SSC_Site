from django.contrib import admin
from subprocess_manager.models import Subprocess

class SubprocessAdmin(admin.ModelAdmin):
    fields = ('command', 'shell', 'timeout', 'stdin', 'stdout', 'stderr', 'status')
    readonly_fields = ('stdout', 'stderr', 'status')
    list_display = ('command', 'shell', 'timeout', 'stdin', 'stdout', 'stderr', 'status')

admin.site.register(Subprocess, SubprocessAdmin)