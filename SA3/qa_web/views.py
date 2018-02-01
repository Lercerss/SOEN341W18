from django.shortcuts import render, HttpResponse
from .models import Post


def index(request):
    return render(request, 'qa_web/index.html', context={'posts': Post.objects.all()})
