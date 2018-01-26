from django.conf import settings


def custom(request):
    return {'site_url': settings.SITE_URL}
