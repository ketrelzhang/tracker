from django.conf.urls import url, include
from web.views import account
from django.contrib import admin

urlpatterns = [
    url(r'^register/$', account.register, name='register'),
]