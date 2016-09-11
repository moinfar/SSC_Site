import csv
import os
import zipfile
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from pip._vendor.distlib._backport import shutil
import tempita
from certificates.models import Certificate
from mezzanine.conf import settings


def download_certificate(request, cid, *args, **kwargs):
    if not request.user.has_perm('certificates.download'):
        raise Http404
    cert = get_object_or_404(Certificate, id=cid)
    data_path = os.path.join(settings.MEDIA_ROOT, cert.data.path)
    with open(data_path) as data_file:
        # unzip template files
        template_path = os.path.join(settings.MEDIA_ROOT, cert.template.path)
        output_dir = os.path.join(os.path.dirname(template_path), os.path.basename(template_path) + '.tmp')
        shutil.rmtree(output_dir)
        os.mkdir(output_dir)
        template_zip = zipfile.ZipFile(template_path)
        template_zip.extractall(output_dir)
        # render main.tex
        reader = csv.reader(data_file)
        main_tex_path = os.path.join(output_dir, 'main.tex')
        with open(main_tex_path) as main_tex_file:
            main_tex = main_tex_file.read()
            template = tempita.Template(main_tex, name='main.tex')
            rendered = template.substitute(rows=reader)
        os.remove(main_tex_path)
        with open(main_tex_path, 'w') as main_tex_file:
            main_tex_file.write(rendered)
        # compile main.tex

        return HttpResponse(rendered)

    # lock, unzip, compile, download
