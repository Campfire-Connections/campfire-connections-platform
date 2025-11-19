from django.shortcuts import render
from django.http import HttpResponse


def healthcheck(request):
    return HttpResponse("ok")


def home(request):
    return render(request, "home.html")
