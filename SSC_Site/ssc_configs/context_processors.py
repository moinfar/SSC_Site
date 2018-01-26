from SSC_Site import settings


def custom(request):
    return {'site_url': settings.SITE_URL}