import random
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings

from django_redis import get_redis_connection

from web import models
from utils.tencent.sms import send_sms_single
from utils import encrypt


class RegisterModelForm(forms.ModelForm):

    mobile_phone = forms.CharField(
        label='Mobile Number', validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', 'Wrong number'), ])

    password = forms.CharField(
        label='Password',
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "At least 8 characters",
            'max_length': "At most 64 characters"
        },
        widget=forms.PasswordInput())

    confirm_password = forms.CharField(
        label='Confirm Password',
        min_length=8,
        max_length=64,
        error_messages={
            'min_length': "At least 8 characters",
            'max_length': "At most 64 characters"
        },
        widget=forms.PasswordInput())

    verify_code = forms.CharField(label='Verify Code', widget=forms.TextInput())

    class Meta:
        model = models.UserInfo
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', 'verify_code']

    # control input form style
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '%s' % (field.label,)

    def clean_username(self):
        username = self.cleaned_data['username']
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('The username is already existed.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('The email is already existed.')
        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        # encrypt password
        return encrypt.md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm_pwd = encrypt.md5(self.cleaned_data['confirm_password'])
        if pwd != confirm_pwd:
            raise ValidationError('The two passwords do not match.')
        return confirm_pwd

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone='mobile_phone').exists()
        if exists:
            raise ValidationError('The number is already registered.')
        return mobile_phone

    def clean_verify_code(self):
        verify_code = self.cleaned_data['verify_code']

        mobile_phone = self.cleaned_data.get('mobile_phone')
        if not mobile_phone:
            return verify_code

        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('The code is invalid, please retry.')

        redis_str_code = redis_code.decode('utf-8')
        if verify_code.strip() != redis_str_code:
            raise ValidationError('The verification code is wrong.')
        return verify_code


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
