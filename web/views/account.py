"""
account information
"""
from django.shortcuts import render, HttpResponse
from web import models
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSMSForm
from django.conf import settings
from django.http import JsonResponse


def register(request):
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'register.html', {'form': form})

    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        # write into DB (password should be encrypted)
        form.save()
        return JsonResponse({'status': True, 'data': '/login/'})
    return JsonResponse({'status': False, 'error': form.errors})


def send_sms(request):
    """ Send SMS """
    form = SendSmsForm(request, data=request.GET)
    # Check if the phone number is empty or the format is correct
    if form.is_valid():
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def login_sms(request):
    """login via sms"""
    if request.method == 'GET':
        form = LoginSMSForm()
        return render(request, 'login_sms.html', {'form': form})

    form = LoginSMSForm(request.POST)
    if form.is_valid():
        # If the detail is correct
        mobile_phone = form.cleaned_data['mobile_phone']
        # Write username into session
        user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        request.session['user_id'] = user_object.id
        request.session['user_name'] = user_object.username
        return JsonResponse({'status': True, 'data': "/index/"})
    return JsonResponse({'status': False, 'error': form.errors})



