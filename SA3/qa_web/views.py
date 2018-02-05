from django.shortcuts import render, HttpResponse
from .models import Post
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'qa_web/index.html', context={'posts': Post.objects.all()})


@csrf_exempt
def user_login(request):
    return render_to_response('qa_web/login.html')
