from django.shortcuts import render, HttpResponse

# Create your views here.
import random
from utils.tencent.sms import send_sms_single
from django.conf import settings


def send_sms(request):
    """send message
        ?tpl = login -->  743590
        ?tpl = register -->  743589
        ?tpl = reset  --> 743591
    """
    tpl = request.GET.get('tpl')
    template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
    if not template_id:
        return HttpResponse('The template does not exist.')

    code = random.randrange(1000, 9999)
    res = send_sms_single('17317271175', 743589, [code, ])
    if res['result'] == 0:
        return HttpResponse('Success')
    else:
        return HttpResponse(res['errmsg'])
