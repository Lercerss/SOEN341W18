from django.shortcuts import render
from .models import Post
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from .forms import LoginForm
from django.http import HttpResponseRedirect


def index(request):
    return render(request, 'qa_web/index.html', context={'posts': Post.objects.all()})


@csrf_exempt
def user_login(request):
    return render_to_response('qa_web/login.html')


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
