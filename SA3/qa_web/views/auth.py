"""
Controller for registration and authentication operations
"""

from django.contrib import auth
from django.shortcuts import render, render_to_response, \
    HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from qa_web.forms import LoginForm, CustomUserCreationForm


@csrf_exempt
def login(request):
    """Displays the login form on a GET request, otherwise validates and signs
    in the user on a POST.

    :param request: Request data provided by the WSGI
    :return: Rendered template displaying the login form on a GET or
            unsuccessful validation, else redirects to given `next` parameter
            or website index.
    """
    if request.method == 'GET':
        form = LoginForm()
        return render_to_response('qa_web/login.html', context={'form': form})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                # Use parameter from login_required decorator to redirect to a
                # specific page, otherwise index
                return HttpResponseRedirect(request.GET.get('next', '/'))
            else:
                return render_to_response('qa_web/login.html',
                                          context={'form': form,
                                                   'password_is_wrong': True})
        else:
            return render_to_response('qa_web/login.html',
                                      context={'form': form})


def logout_view(request):
    """Logs out the user and redirects to login

    :param request: Request data provided by the WSGI
    :return: Redirect to login page
    """
    auth.logout(request)
    return HttpResponseRedirect('/login/')


@csrf_exempt
def signup(request):
    """Displays the signup form on a GET, otherwise redirects to the home page
    on a successful signup.

    :param request: Request data provided by the WSGI
    :return: Rendered template displaying the signup form on a GET or
            unsuccessful validation, else redirects to the homepage
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=raw_password)
            auth.login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'qa_web/sign_up.html', {'form': form})
