import json
import hashlib

from mezzanine.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from mezzanine.pages.page_processors import processor_for

from .models import ScreenPage


@processor_for(ScreenPage)
def screen_page_processor(request, page):
    if request.GET.get('view'):
        if request.GET.get('view') == 'all':
            return {'show': 'all'}
        elif request.GET.get('view') == 'recent':
            return {'show': 'recent'}
        elif request.GET.get('view') == 'full_screen':
            return render(request, 'pages/full_screen_screenpage.html', {'page': page})
        elif request.GET.get('view') == 'json':
            current_images = page.screenpage.current_images()
            images = []
            for screen_image in current_images:
                if screen_image.image:
                    images += [dict(content=screen_image.content,
                                    image="%s%s" % (settings.MEDIA_URL, screen_image.image))]
                else:
                    images += [dict(content=screen_image.content, image=None)]

            hash = hashlib.md5(json.dumps(images, ensure_ascii=True)).hexdigest()

            result = json.dumps({'status': 'OK', 'hash': hash, 'images': images}, ensure_ascii=False, encoding='utf8')
            return HttpResponse(result, content_type='application/json; charset=utf-8')

    return {'show': 'recent'}
