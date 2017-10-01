import csv
import os
import zipfile
from django.core.files import File
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import shutil
import tempita
from certificates.models import Certificate
from mezzanine.conf import settings

XELATEX_PATH = getattr(settings, 'XELATEX_PATH', 'xelatex')


def compile_certificate(request, cid, *args, **kwargs):
    if not request.user.has_perm('certificates.can_compile'):
        raise Http404
    cert = get_object_or_404(Certificate, id=cid)
    data_path = os.path.join(settings.MEDIA_ROOT, cert.data.path)
    with open(data_path) as data_file:
        template_path = os.path.join(settings.MEDIA_ROOT, cert.template.path)
        output_dir = os.path.join(os.path.dirname(template_path),
                                  os.path.basename(template_path) + '.tmp')
        main_tex_path = os.path.join(output_dir, 'main.tex')
        compile_command = '%s -halt-on-error -output-directory=%s %s' % (
        XELATEX_PATH, output_dir, main_tex_path)
        p = cert.compile_process
        p.command = compile_command
        p.shell = False
        p.status = 'N'
        p.stdout = ''
        p.stderr = ''
        p.save()
        # unzip template files
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.mkdir(output_dir)
        template_zip = zipfile.ZipFile(template_path)
        template_zip.extractall(output_dir)
        # render main.tex
        reader = csv.reader(data_file)
        with open(main_tex_path) as main_tex_file:
            main_tex = main_tex_file.read()
            template = tempita.Template(main_tex, name='main.tex')
            rendered = template.substitute(rows=reader)
        os.remove(main_tex_path)
        with open(main_tex_path, 'w') as main_tex_file:
            main_tex_file.write(rendered)
        # compile main.tex
        p.run(wait=True)
        output_path = os.path.join(output_dir, 'main.pdf')
        filename = 'certificates/out/cert_%d.pdf' % cert.id
        shutil.move(output_path, os.path.join(settings.MEDIA_ROOT, filename))
        shutil.rmtree(output_dir)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
