from django.conf.urls import url, include
from web.views import account
from django.contrib import admin

urlpatterns = [
    url(r'^register/$', account.register, name='register'),
    url(r'^login/sms/$', account.login_sms, name='login_sms'),  # login via sms
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
]