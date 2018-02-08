from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path(r'login/', views.login, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    path('questions', views.questions, name='questions'),
    path('answers', views.answers, name='answers')
]
