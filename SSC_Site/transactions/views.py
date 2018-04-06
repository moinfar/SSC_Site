from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.utils.translation import ugettext as _
from transactions.models import PriceGroup, DiscountCode


def check_discount_code(request):
    code = request.POST.get('code')
    price_group_id = request.POST.get('plan')
    if not code or not price_group_id or not price_group_id.isnumeric():
        return JsonResponse({'error': _('Invalid data or plan id')}, status=400)
    price_group = get_object_or_404(PriceGroup, id=int(price_group_id))
    out = price_group.validate_discount_code(code)
    if 'error' in out:
        return JsonResponse(out, status=400)
    return JsonResponse(out)
