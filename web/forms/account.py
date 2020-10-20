from django import forms
from web import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings
import random
from utils.tencent.sms import send_sms_single
from django_redis import get_redis_connection


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
            field.widget.attrs['placeholder'] = 'Please Input %s' % (field.label,)


class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(
        label='Mobile Number', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', 'Wrong Number'), ])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        """ Check Phone number """
        mobile_phone = self.cleaned_data['mobile_phone']

        # Check if the template of phone number is correct
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError('Wrong Template.')

        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if tpl == 'login':
            if not exists:
                raise ValidationError('The number can by used.')
        else:
            # Check if the phone is already existed
            if exists:
                raise ValidationError('The number is existed.')

        code = random.randrange(1000, 9999)

        # Send sms
        sms = send_sms_single(mobile_phone, template_id, [code, ])
        if sms['result'] != 0:
            raise ValidationError("Send failed，{}".format(sms['errmsg']))

        # Write Verify Code into redis（django-redis）
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)

        return mobile_phone
