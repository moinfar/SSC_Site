import signal
import subprocess
import threading

import os
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Subprocess(models.Model):
    STATUS_CHOICES = (
        ('N', _('New')),
        ('R', _('Running')),
        ('S', _('Success')),
        ('E', _('Error')),
        ('T', _('Timeout')),
    )

    command = models.TextField(verbose_name=_("Command"), blank=True)
    shell = models.BooleanField(verbose_name=("Shell"), default=False)
    timeout = models.IntegerField(verbose_name=_("Timeout (s)"), default=0)
    stdin = models.TextField(verbose_name=_("Input"), blank=True)
    stdout = models.TextField(verbose_name=_("Output"), blank=True, editable=False)
    stderr = models.TextField(verbose_name=_("Errors"), blank=True, editable=False)
    status = models.CharField(verbose_name=_("Status"), choices=STATUS_CHOICES, default='N',
                              editable=False, max_length=1)
    pid = models.CharField(verbose_name=_("Process ID"), blank=True, editable=False, max_length=10)

    def run(self, wait=False):
        if self.status != 'N':
            return None
        try:
            self.status = 'R'
            self.save()
            p = subprocess.Popen(self.command.split(),
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            self.pid = p.pid
            self.save()

            class Communicator(threading.Thread):
                def run(s):
                    (out, err) = p.communicate(self.stdin)
                    self.stdout = out.decode('utf-8')
                    self.stderr = err.decode('utf-8')
                    self.status = 'E' if p.returncode else 'S'
                    self.save()

            class Terminator(threading.Thread):
                def run(s):
                    threading._sleep(self.timeout)
                    p.kill()

            communicator = Communicator()
            communicator.start()
            if wait:
                communicator.join()
            if self.timeout > 0:
                terminator = Terminator()
                terminator.start()
            return p

        except Exception as e:
            self.status = 'E'
            self.stderr = str(e.args)
            self.save()

    def kill(self):
        return os.kill(self.pid, signal.SIGKILL)
