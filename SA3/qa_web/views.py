from .models import Post, Questions
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from .forms import LoginForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def index(request):
    return render(request, 'qa_web/index.html', context={'posts': Post.objects.all()})


# def signup_test(request):
#     form = UserCreationForm()
#     return render_to_response('qa_web/sign_up.html', context={'form': form})  # for testing login page.

@csrf_exempt
def login(request):
    if request.method == 'GET':
        form = LoginForm()
        # return render_to_response('qa_web/login.html', RequestContext(request, {'form': form, }))
        return render_to_response('qa_web/login.html', context={'form': form})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                # return render_to_response('qa_web/index.html')
                return HttpResponseRedirect('/')
                # jumping to index page means login successful
            else:
                return render_to_response('qa_web/login.html', context={'form': form, 'password_is_wrong': True})
        else:
            return render_to_response('qa_web/login.html', context={'form': form})


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth.login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'qa_web/sign_up.html', {'form': form})


def questions(request):
    # REceive get request

    # Take care of post requests
    content = '' # retrieve from request
    title = ''
    question = Questions(content, title)
    question.save()
    return render(request, 'qa_web/questionspage.html', context={})

def answers(request):
    return render(request, 'qa_web/answerspage.html', context={})
