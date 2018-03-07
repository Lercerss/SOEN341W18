from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [

    path(r'login/', views.login, name='login'),
    path(r'logout/', views.logout_view, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    path('questions/', views.questions, name='questions'),
    path('questions/<int:id_>/', views.answers, name='answers'),
    url(r'^$', views.homepage, name='homepage'),
    path('vote/', views.vote, name='vote'),
    path('questions/<int:id_>/edit/', views.edit, name='edit'),
    url(r'QuestionIndex/', views.QuestionDisplayView.as_view(), name='QuestionIndex'),
    url(r'^tag/(?P<tag>[-\w]+)/$', views.QuestionsByTagView.as_view(), name='question_by_tag'),
    path('editprofile/', views.edit_profile, name='UserProfile'),
    path('profile/<int:id_>/', views.display_profile, name='UserProfile'),
]
