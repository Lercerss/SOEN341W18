from django.contrib import admin
from django.urls import path
from qa_web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('questions/', views.questions, name='questions'),
    path('questions/<int:id_>/', views.answers, name='answers'),
    path('', views.homepage, name='homepage'),
    path('vote/', views.vote, name='vote'),
    path('questions/<int:id_>/edit/', views.edit, name='edit'),
    path('question_index/', views.QuestionDisplayView.as_view(), name='question_index'),
    path('tag/<str:tag>/', views.QuestionsByTagView.as_view(), name='question_by_tag'),
    path('edit_profile/', views.edit_profile, name='edit_user_profile'),
    path('profile/<int:id_>/', views.display_profile, name='display_user_profile'),
    path('questions/<int:id_>/delete/', views.delete, name='delete_question'),
]
