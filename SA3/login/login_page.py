__author__ = 'will'
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, Django.")