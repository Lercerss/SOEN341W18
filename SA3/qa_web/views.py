from .models import Answers, Questions, User
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from .forms import LoginForm, QuestionsForm, AnswersForm
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields


def index(request):
    # return render(request, 'qa_web/index.html', context={'posts': Post.objects.all()})
    return render(request, 'qa_web/index.html', context={'questions': Questions.objects.all()})


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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth.login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'qa_web/sign_up.html', {'form': form})


@login_required(login_url='/login/')
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
        else:
            return render(request, 'qa_web/questionspage.html', context={})


def answers(request, id_):
    q = get_object_or_404(Questions, pk=id_)
    if request.method == 'POST' and 'answer_form' in request.POST: #Update's database when somebody answers a question
        form = AnswersForm(request.POST)
        if form.is_valid(): 
            Answers.objects.create(content=request.POST['content'], owner=request.user, question=q)
    elif request.method == 'POST' and 'deselect' in request.POST:  #Update's database when somebody deselects best answer.
        updateAnswer = Answers.objects.filter(question=q, correct_answer=True).last()
        updateAnswer.correct_answer = False;
        updateAnswer.save();
    else: #Update's database when somebody selects a best answer.
        q_answers = Answers.objects.filter(question=q, correct_answer=False)
        for answer in q_answers:
            if request.method == 'POST' and 'select_'+str(answer.id) in request.POST:
                updateAnswer = Answers.objects.get(id = answer.id)
                updateAnswer.correct_answer = True;
                updateAnswer.save();
    #Get updated answer data.
    q_answers = Answers.objects.filter(question=q, correct_answer=False)
    q_best_answer = Answers.objects.filter(question=q, correct_answer=True)
    return render(request, 'qa_web/answerspage.html', {'currentQuestion': q, 'answers': q_answers, 'bestAnswer': q_best_answer})


# Home Page
def homepage(request):
    return render(request, "qa_web/home.html")
