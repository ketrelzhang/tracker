from django.shortcuts import render, HttpResponse

# Create your views here.
import random
from utils.tencent.sms import send_sms_single
from django.conf import settings
from django import forms
from app01 import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


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


class RegisterModelForm(forms.ModelForm):

    mobile_phone = forms.CharField(
        label='Mobile Number', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', 'Wrong number'), ])
    password = forms.CharField(label='Password', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())
    verify_code = forms.CharField(label='Verify Code', widget=forms.TextInput())

    class Meta:
        model = models.UserInfo
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', 'verify_code']

    # control input form style
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = 'Please input %s' % (field.label,)


def register(request):
    form = RegisterModelForm()
    return render(request, 'app01/register.html', {'form': form})
