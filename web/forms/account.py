from django import forms
from web import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


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
            field.widget.attrs['placeholder'] = '%s' % (field.label,)