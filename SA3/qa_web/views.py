from .models import Post, Questions
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from .forms import LoginForm, QuestionsForm
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required


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


@login_required
def questions(request):
    if request.method == 'GET':
        return render(request, 'qa_web/questionspage.html', context={})
    else:
        form = QuestionsForm(request.POST)
        if form.is_valid():
            content = request.POST['content']
            title = request.POST['title']
            owner = request.user
            q = Questions(content=content, title=title, owner=owner)
            q.save()
            return HttpResponseRedirect('/questions/{q.id}/'.format(q=q))


def answers(request, id):
        q = get_object_or_404(Questions, pk=id)
        return render(request, 'qa_web/answerspage.html', {'currentQuestion': q})

