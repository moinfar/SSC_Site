from mezzanine.core.tests import TestCase
from subprocess_manager.models import Subprocess


class SubprocessTest(TestCase):
    def test_echo(self):
        p = Subprocess.objects.create(command='echo hello', shell=True)
        p.run(wait=True)
        self.assertEqual(p.stdout, 'hello')
