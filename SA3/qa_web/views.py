from .models import Answers, Questions, User, Comments, Vote
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from .forms import LoginForm, QuestionsForm, AnswersForm, EditForm, UserProfile
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponseForbidden
from django.contrib.auth import login, authenticate, get_user_model, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from .forms import UploadProfilePicForm
from django.db.models import Count, F
from taggit.models import Tag, TaggedItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.contenttypes.models import ContentType

from django.contrib import messages


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields

@login_required(login_url='/login/')
def edit_profile(request):
    if request.method=='GET':
        form = UserProfile()
        # return render_to_response('qa_web/UserProfile.html', RequestContext(request, {'form': form, }))
        return render(request,'qa_web/EditUserProfile.html', context={'form': form})
    else:
        form = UserProfile(request.POST, request.FILES)
        # validating the form occurs below and then saving the results entered by the user
        if form.is_valid():
            user = request.user

            user.first_name = request.POST['prename']
            user.last_name = request.POST['surname']
            user.age = request.POST['age']
            user.email = form.cleaned_data.get('email')
            user.birthday = form.cleaned_data.get('birthday')
            user.motherland = request.POST['motherland']
            user.school = request.POST['school']
            user.major = request.POST['major']
            user.city = request.POST['city']
            user.image = form.cleaned_data.get('image')

            user.save()

            # when the information is entered and the information is saved
            # the page gets redirected to the profile page
            return HttpResponseRedirect('/profile/{}/'.format(user.id))
        else:
            return render(request, 'qa_web/EditUserProfile.html', context={'form': form})


def display_profile(request, id_):
    displayed_user = get_object_or_404(User, pk=id_)
    user_qs = Questions.objects.filter(owner_id=id_)
    user_as = Answers.objects.filter(owner_id=id_)
    user_vs = Vote.objects.filter(user_id=id_)
    return render(request, 'qa_web/UserProfile.html', context={'displayed_user': displayed_user,
                                                               'questions': user_qs,
                                                               'answers': user_as,
                                                               'votes': user_vs})





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
                # Use parameter from login_required decorator to redirect to a specific page, otherwise index
                return HttpResponseRedirect(request.GET.get('next', '/'))
            else:
                return render_to_response('qa_web/login.html', context={'form': form, 'password_is_wrong': True})
        else:
            return render_to_response('qa_web/login.html', context={'form': form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('../login/')
    # redirects to log in page once logged out successfully

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
            tag = request.POST['tag'].split(';')
            owner = request.user
            q = Questions(content=content, title=title, owner=owner)
            q.save()
            [q.tag.add(each_tag) for each_tag in tag if each_tag.strip() != '']
            # since question can be submitted with no tag, filtering empty and blank string.
            return HttpResponseRedirect('/questions/{q.id}/'.format(q=q))
        else:
            return render(request, 'qa_web/questionspage.html', context={})


def answers(request, id_):
    q = get_object_or_404(Questions, pk=id_)
    answer_id = [int(key.replace('select_', '')) for key in request.POST.keys() if key.startswith('select_')]
    if request.method == 'POST' and 'answer_form' in request.POST: #Update's database when somebody answers a question
        form = AnswersForm(request.POST)
        if form.is_valid():
            Answers.objects.create(content=request.POST['content'], owner=request.user, question=q)
    elif request.method == 'POST' and 'deselect' in request.POST:  #Update's database when somebody deselects best answer.
        updateAnswer = Answers.objects.filter(question=q, correct_answer=True).last()
        updateAnswer.correct_answer = False
        updateAnswer.save()
    elif answer_id: #Update's database when somebody selects a best answer.
        updateAnswer = Answers.objects.get(id = answer_id[0])
        updateAnswer.correct_answer = True
        updateAnswer.save()
    elif any(key.startswith("comment_form_answer") for key in request.POST.keys()):
        answer_id = [int(key.replace('comment_form_answer_', '')) for key in request.POST.keys() if key.startswith('comment_form')]
        a = Answers.objects.get(id = answer_id[0])
        c = Comments(content=request.POST['content'], owner=request.user, answer=a)
        c.save()
    elif request.method == 'POST' and 'comment_form_question' in request.POST:
        q = Questions.objects.get(id = q.id)
        c = Comments(content=request.POST['content'], owner=request.user, question=q)
        c.save()

    #Get updated answer data
    q_answers = Answers.objects.filter(question=q, correct_answer=False).annotate(points=F('upvotes')-F('downvotes')).order_by('-points') #Most points first.

    if request.method == 'POST' and 'sort_by_form_select' in request.POST:
        initialSelectValue = request.POST['sort_by_form_select']
        if request.POST['sort_by_form_select'] == 'lowestScore':
            q_answers = Answers.objects.filter(question=q, correct_answer=False).annotate(points=F('upvotes')-F('downvotes')).order_by('points')
        elif request.POST['sort_by_form_select'] == 'highestScore':
            q_answers = Answers.objects.filter(question=q, correct_answer=False).annotate(points=F('upvotes')-F('downvotes')).order_by('-points')
        elif request.POST['sort_by_form_select'] == 'leastRecent':
            q_answers = Answers.objects.filter(question=q, correct_answer=False).order_by('creation_date')
        else: #Most Recent
            q_answers = Answers.objects.filter(question=q, correct_answer=False).order_by('-creation_date')
    else:
         initialSelectValue = "highestScore"
         q_answers = Answers.objects.filter(question=q, correct_answer=False).annotate(points=F('upvotes')-F('downvotes')).order_by('-points')


    q_best_answer = Answers.objects.filter(question=q, correct_answer=True)
    q_comments = Comments.objects.filter(question=q)
    a_comments = Comments.objects.filter(answer__question=q)

    #Increment the visits counter of the question by one
    if request.user.is_authenticated:
        q.visits += 1
        q.save()

    if len(q_best_answer) > 0:
        q_best_answer = q_best_answer.last()
    return render(request, 'qa_web/answerspage.html', {'currentQuestion': q, 'answers': q_answers, 'bestAnswer': q_best_answer, 'q_comments': q_comments, 'a_comments': a_comments, 'initial_select_value': initialSelectValue})


def vote(request):
    """Receives Ajax queries to vote on Posts, updates the corresponding Post and returns the new score"""
    if request.method == 'POST' and request.user.is_authenticated:
        vote_direction, button_id, post_type = request.POST['button'].split('_')
        vote_direction = vote_direction == 'upvote'
        post_subclass = Questions if post_type == 'question' else Answers if post_type == 'answer' else Comments
        post = get_object_or_404(post_subclass, pk=int(button_id))
        foreign_key_args = {post_type:post} # Workaround to provide the correct kwarg depending on post_type
        if request.user not in post.voters.all():
            # Add user's vote
            Vote.objects.create(user=request.user, positive=vote_direction,
                                    **foreign_key_args) # Bind the post to the appropriate FK
            if vote_direction:
                post.upvotes = post.upvotes + 1
            else:
                post.downvotes = post.downvotes + 1
        else:
            # Allow user to modify their vote
            last_vote = Vote.objects.get(user=request.user, **foreign_key_args)
            if last_vote.positive == vote_direction:
                # Vote cancelled, user pressed same button as original vote
                last_vote.delete()
                if vote_direction:
                    post.upvotes = post.upvotes - 1
                else:
                    post.downvotes = post.downvotes - 1
            else:
                # Vote changed direction
                last_vote.positive = vote_direction
                last_vote.save()
                if vote_direction:
                    post.upvotes = post.upvotes + 1
                    post.downvotes = post.downvotes - 1
                else:
                    post.downvotes = post.downvotes + 1
                    post.upvotes = post.upvotes - 1
        post.save()
        return JsonResponse({'new_score' : post.score, 'id' : 'score_{}_{}'.format(post.id, post_type)})
    # Accessing url without using Post or unauthenticated
    return HttpResponseRedirect('/')


# Home Page
def homepage(request):
    return render(request, "qa_web/home.html")

class QuestionDisplayView(ListView):
    model = Questions
    paginate_by = 10  # 10 questions a page
    context_object_name = 'questions'
    template_name = 'qa_web/question_display_page.html'
    ordering = '-creation_date'

    def get_context_data(self, *args, **kwargs):
        context = super(
            QuestionDisplayView, self).get_context_data(*args, **kwargs)

        context['total_question_num'] = Questions.objects.count()
        context['total_answer_num'] = Answers.objects.count()

        #  try to page the question page
        context['is_paginated'] = True  # whether the paginator is needed. It's a must.
        all_questions_qs = Questions.objects.order_by('-creation_date')\
            .select_related('owner')\
            .annotate(num_answers=Count('answers', distinct=True),
                      num_question_comments=Count('comments', distinct=True),
                      num_tag=Count('tag', distinct=True))
        paginator_all_questions = Paginator(all_questions_qs, QuestionDisplayView.paginate_by)

        # get question_page number from url
        page_0 = self.request.GET.get('question_page')
        try:
            page_obj = paginator_all_questions.page(page_0)

        except PageNotAnInteger:
            page_obj = paginator_all_questions.page(1)

        except EmptyPage:  # pragma: no cover
            page_obj = paginator_all_questions.page(paginator_all_questions.num_pages)
        # page_obj = paginator_all_questions.page(1)
        context['latest_current_page'] = page_obj

        # using modified paging num
        pagination_data = self.pagination_data(paginator_all_questions, page_obj, context['is_paginated'])
        context.update(pagination_data)

        # Debug: to inspect each page object in current page.
        # for page_ in page_obj:  #  inspect structure of page_
        #     print(len(page_.tag.all()))
        #     print(page_.num_tag)
        #     for each in page_.tag.all():
        #         print(each.slug)

        # To-do: second tab: unanswered page
        # un_answered page, aggregate attributes num_answers and num_question_comments to this QuerySet
        un_answered_qs = Questions.objects.order_by('-creation_date')\
            .filter(answers__isnull=True).select_related('owner')\
            .annotate(num_answers=Count('answers', distinct=True),
                      num_question_comments=Count('comments',
                      distinct=True))
        paginator = Paginator(un_answered_qs, QuestionDisplayView.paginate_by)

        # make this tab active
        context['active_tab'] = self.request.GET.get('active_tab', 'latest')
        tabs = ['latest', 'un_answered']
        context['active_tab'] = 'latest' if context['active_tab'] not in\
            tabs else context['active_tab']

        page_index = self.request.GET.get('un_answered_page')
        try:
            un_answered_page = paginator.page(page_index)

        except PageNotAnInteger:
            un_answered_page = paginator.page(1)

        except EmptyPage:  # pragma: no cover
            un_answered_page = paginator.page(paginator.num_pages)

        context['un_answered_num_for_current_page'] = paginator.count
        context['un_answered_page'] = un_answered_page

        # pass tags to html.
        question_contenttype = ContentType.objects.get_for_model(Questions)
        items = TaggedItem.objects.filter(content_type=question_contenttype)
        context['tags'] = Tag.objects.filter(
            taggit_taggeditem_items__in=items).exclude(slug__exact='').order_by('-id').distinct()

        return context

    def get_queryset(self):
        queryset = super(QuestionDisplayView, self).get_queryset()\
            .select_related('owner')\
            .annotate(num_answers=Count('answers', distinct=True),
                      num_question_comments=Count('comments',
                      distinct=True))
        return queryset

    def pagination_data(self, paginator, page, is_paginated):
        """to show page number like this:
         1...3 4 5- 6 7 ...9
         1...3 4 5- 6 7
         1 2 3-
         """

        if not is_paginated:
            # if no pagination, no more data needed.
            return {}

        # current page's left page num.
        left = []

        # current page's right page num.
        right = []

        # if ellipsis is needed right to the first page.
        left_has_more = False

        # if ellipsis is needed left to the final page.
        right_has_more = False

        # whether to show 1 page number if it's near the current page, like: 1 2 3, not 1...1 2 3
        first = False
        last = False

        # current page number
        page_number = page.number

        total_pages = paginator.num_pages

        # total page range, like [1, 2, 3, 4]
        page_range = paginator.page_range

        if page_number == 1:
            # no need left page data, left=[]
            # get right page information [1, 2, 3, 4]，so right = [2, 3]
            right = page_range[page_number:page_number + 2]
            if len(right) == 0:
                return {}

            if right[-1] < total_pages - 1:
                right_has_more = True

            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

            if len(left) != 0 and left[0] > 2:
                left_has_more = True

            if len(left) != 0 and left[0] > 1:
                first = True
        else:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

        if len(left) != 0 and left[0] > 2:
            left_has_more = True
        if len(left) != 0 and left[0] > 1:
            first = True

        context = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return context


class QuestionsByTagView(ListView):
    """View to call all the questions classified under one specific tag.
    """
    model = Questions
    paginate_by = 10
    context_object_name = 'questions'
    template_name = 'qa_web/question_display_page.html'

    def get_queryset(self, **kwargs):
        # that's why we should use regex group name in url: url(r'^tag/(?P<tag>[-\w]+)/$'. A common way to get
        # parameters from front end.
        return Questions.objects.order_by('-creation_date').filter(tag__slug=self.kwargs['tag'])\
                                .annotate(num_answers=Count('answers', distinct=True))

    def get_context_data(self, *args, **kwargs):
        context = super(
            QuestionsByTagView, self).get_context_data(*args, **kwargs)

        # get default display objects from get_queryset.
        context['latest_current_page'] = context['questions']

        context['active_tab'] = self.request.GET.get('active_tab', 'latest')
        tabs = ['latest', 'un_answered']  # to-do: un_answered tag
        context['active_tab'] = 'latest' if context['active_tab'] not in\
            tabs else context['active_tab']

        context['total_question_num'] = Questions.objects.count()
        context['total_answer_num'] = Answers.objects.count()

        # another way to get tagged questions if not get from get_queryset.
        context['un_answered_page'] = Questions.objects.order_by('-creation_date').filter(
            tag__name__contains=self.kwargs['tag'], answers__isnull=True)
        context['total_un_answered_page_num'] = len(context['un_answered_page'])
        return context


# edit post
@login_required(login_url='/login/')
def edit(request, id_):

    q = get_object_or_404(Questions, pk=id_)
    if q.owner != request.user:
        return HttpResponseForbidden()

    form = EditForm(request.POST)
    if request.POST and form.is_valid():
        q.content = request.POST['content']
        q.title = request.POST['title']
        q.owner = request.user
        q.save()
        return HttpResponseRedirect('/questions/{q.id}/'.format(q=q))
    return render(request,'qa_web/edit.html', context={'post':q, 'isAnswer': False})


#delete posts
@login_required(login_url='/login/')
def delete(request, id_):
    q = get_object_or_404(Questions, pk=id_)
    if q.owner != request.user:
        return HttpResponseForbidden()
    q.delete()
    return HttpResponseRedirect('/QuestionIndex')


# edit Answers
@login_required(login_url='/login/')
def edit_answers(request, id_, a_id):

    a = get_object_or_404(Answers, pk=a_id)
    if a.owner != request.user:
        return HttpResponseForbidden()

    form = EditForm(request.POST)
    if request.POST and form.is_valid():
        a.content = request.POST['content']
        a.owner = request.user
        a.save()
        return HttpResponseRedirect('/questions/{id}/'.format(id=id_))
    return render(request,'qa_web/edit.html', context={'post':a, 'is_answer': True})




