"""
account information
"""
from django.shortcuts import render, HttpResponse
from web import models
from web.forms.account import RegisterModelForm, SendSmsForm
from django.conf import settings
from django.http import JsonResponse


def register(request):
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'register.html', {'form': form})

    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        # write into DB (password should be encrypted)
        instance = form.save()
        return JsonResponse({'status': True, 'data': '/login/'})
    return JsonResponse({'status': False, 'error': 'form.errors'})


def send_sms(request):
    """ Send SMS """
    form = SendSmsForm(request, data=request.GET)
    # Check if the phone number is empty or the format is correct
    if form.is_valid():
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})
