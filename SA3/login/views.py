from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django import forms
from django.views.decorators.csrf import csrf_exempt

class UserForm(forms.Form):
    username = forms.CharField(label='Username:', max_length=100)
    password = forms.CharField(label='Password:', widget=forms.PasswordInput())


@csrf_exempt
def index(request):
    form_ = UserForm()  # given an empty form for now. just to show the login page.
    return render_to_response('login.html', locals())

# Create your views here.
