from django.shortcuts import render, HttpResponse


# here are views stored


def home(request):
    return HttpResponse("This is aweseome!")