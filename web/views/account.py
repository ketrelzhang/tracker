"""
account information
"""
from django.shortcuts import render, HttpResponse
from web.forms.account import RegisterModelForm, SendSmsForm
from django.conf import settings
from django.http import JsonResponse


def register(request):
    form = RegisterModelForm()
    return render(request, 'register.html', {'form': form})


def send_sms(request):
    """ Send SMS """
    form = SendSmsForm(request, data=request.GET)
    # Check if the phone number is empty or the format is correct
    if form.is_valid():
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})
