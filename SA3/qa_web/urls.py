from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path(r'login/', views.login, name='login'),
    url(r'^signup/$', views.signup, name='signup'),
    path('questions/', views.questions, name='questions'),
    path('questions/<int:id_>/', views.answers, name='answers'),
    url(r'^home/$', views.homepage, name='homepage'),
    path('vote/', views.vote, name='vote'),
    url(r'QuestionIndex/', views.QuestionDisplayView.as_view(), name='QuestionIndex'),
]
