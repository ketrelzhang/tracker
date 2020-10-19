"""
account information
"""
from django.shortcuts import render, HttpResponse
from web.forms.account import RegisterModelForm


def register(request):
    form = RegisterModelForm()
    return render(request, 'register.html', {'form': form})


def send_sms(request):
    print(request.GET)

    return HttpResponse("Success")
