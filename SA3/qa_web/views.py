"""Views handle requests sent to the server.
Views are registered to urls, handle a request provided by the WSGI and
return a response.
"""
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.http import HttpResponseRedirect, JsonResponse, \
    HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.db.models import Count, F
from taggit.models import Tag, TaggedItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.contenttypes.models import ContentType
from qa_web.forms import LoginForm, QuestionsForm, AnswersForm, EditForm, \
    UserProfile, CustomUserCreationForm
from qa_web.models import Answer, Question, User, Comment, Vote


@login_required(login_url='/login/')
def edit_profile(request):
    """Displays the user profile editing form on a GET request, on a POST
    validates and saves the user's information.
    Must be logged in to edit one's profile.

    :param request: Request data provided by the WSGI
    :return: Rendered template for editing user template on GET or
             unsuccessful validation.
             Upon successful validation, redirects to the user's profile
    """
    if request.method == 'GET':
        active_user = request.user
        existing_data = {
            'prename': active_user.first_name,
            'surname': active_user.last_name,
            'age': active_user.age,
            'email': active_user.email,
            'birthday': active_user.birthday,
            'motherland': active_user.motherland,
            'school': active_user.school,
            'major': active_user.major,
            'city': active_user.city,
            'image': active_user.image,
        }
        form = UserProfile(initial= existing_data)
        return render(request, 'qa_web/edit_user_profile.html',
                      context={'form': form})
    else:
        form = UserProfile(request.POST, request.FILES)
        if form.is_valid():
            user = request.user

            user.first_name = form.cleaned_data.get('prename')
            user.last_name = form.cleaned_data.get('surname')
            user.age = form.cleaned_data.get('age')
            user.email = form.cleaned_data.get('email')
            user.birthday = form.cleaned_data.get('birthday')
            user.motherland = form.cleaned_data.get('motherland')
            user.school = form.cleaned_data.get('school')
            user.major = form.cleaned_data.get('major')
            user.city = form.cleaned_data.get('city')
            user.image = form.cleaned_data.get('image')

            user.save()

            return HttpResponseRedirect('/profile/{}/'.format(user.id))
        else:
            return render(request, 'qa_web/edit_user_profile.html',
                          context={'form': form})


def display_profile(request, id_):
    """Displays a User's profile information and recent post activity
    Any user can look at a user's profile page

    :param request: Request data provided by the WSGI
    :param id_: The user to be displayed's id
    :return: Rendered template for displaying the given user's profile
    """
    displayed_user = get_object_or_404(User, pk=id_)
    user_questions = Question.objects.filter(owner_id=id_)
    user_answers = Answer.objects.filter(owner_id=id_)
    user_comments = Comment.objects.filter(owner_id = id_)
    return render(request, 'qa_web/user_profile.html',
                  context={'displayed_user': displayed_user,
                           'questions': user_questions,
                           'answers': user_answers,
                           'comments': user_comments})


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


@login_required(login_url='/login/')
def questions(request):
    """Displays the form to post a question or redirects to the question's
    thread once it has been successfully created.
    Requires the user to be logged in.

    :param request: Request data provided by the WSGI
    :return: Rendered template displaying the posting question form on a GET,
            else redirects to the question thread
    """
    if request.method == 'GET':
        return render(request, 'qa_web/posting_question.html', context={})
    else:
        form = QuestionsForm(request.POST)
        if form.is_valid():
            content = request.POST['content']
            title = request.POST['title']
            tag = request.POST['tag'].split(';')
            owner = request.user
            q = Question(content=content, title=title, owner=owner)
            q.save()

            # Since a question can be submitted with no tag, filtering empty
            # and blank strings.
            for each_tag in tag:
                if each_tag.strip() != '':
                    q.tag.add(each_tag)

            return HttpResponseRedirect('/questions/{q.id}/'.format(q=q))
        else:
            return render(request, 'qa_web/posting_question.html', context={})


def answers(request, id_):
    """Manages the different actions that occur when displaying a question:
        - Displaying the question's thread including answers and comments
        - Adding an answer to the question
        - Adding a comment on the question or one of its answers
        - Changing order in which answers are displayed
        - Selecting and deselecting a question's best answer

    :param request: Request data provided by the WSGI
    :param id_: The question's id
    :return: Rendered template displaying the question's thread including
            answers and comments as well as the answering/commenting form
    """
    q = get_object_or_404(Question, pk=id_)
    answer_id = [int(key.replace('select_', ''))
                 for key in request.POST.keys() if key.startswith('select_')]
    if request.method == 'POST' and 'answer_form' in request.POST:
        # Answering a question
        form = AnswersForm(request.POST)
        if form.is_valid():
            Answer.objects.create(
                content=request.POST['content'], owner=request.user, question=q)

    elif request.method == 'POST' and 'deselect' in request.POST and \
            q.owner.id == request.user.id:
        # Deselecting best answer
        update_answer = Answer.objects.filter(
            question=q, correct_answer=True).last()
        update_answer.correct_answer = False
        update_answer.save()
    elif answer_id and q.owner.id == request.user.id:
        # Selecting best answer
        update_answer = Answer.objects.get(id=answer_id[0])
        update_answer.correct_answer = True
        update_answer.save()
    elif any(key.startswith("comment_form_answer") for key in request.POST.keys()):
        # Commenting on an answer
        answer_id = [int(key.replace('comment_form_answer_', '')) for key
                     in request.POST.keys() if key.startswith('comment_form')]
        a = Answer.objects.get(id=answer_id[0])
        c = Comment(content=request.POST['content'],
                    owner=request.user, answer=a)
        c.save()
    elif request.method == 'POST' and 'comment_form_question' in request.POST:
        # Commenting on the question
        c = Comment(content=request.POST['content'],
                    owner=request.user, question=q)
        c.save()

    # Ordering answers
    if request.method == 'POST' and 'sort_by_form_select' in request.POST:
        initial_select_value = request.POST['sort_by_form_select']
        if request.POST['sort_by_form_select'] == 'lowestScore':
            q_answers = Answer.objects.filter(question=q,
                                              correct_answer=False).annotate(
                points=F('upvotes') - F('downvotes')).order_by('points')
        elif request.POST['sort_by_form_select'] == 'highestScore':
            q_answers = Answer.objects.filter(question=q,
                                              correct_answer=False).annotate(
                points=F('upvotes') - F('downvotes')).order_by('-points')
        elif request.POST['sort_by_form_select'] == 'leastRecent':
            q_answers = Answer.objects.filter(
                question=q, correct_answer=False).order_by('creation_date')
        else:  # Most Recent
            q_answers = Answer.objects.filter(
                question=q, correct_answer=False).order_by('-creation_date')
    else:
        initial_select_value = "highestScore"
        q_answers = Answer.objects.filter(question=q,
                                          correct_answer=False).annotate(
            points=F('upvotes') - F('downvotes')).order_by('-points')

    q_best_answer = Answer.objects.filter(question=q, correct_answer=True)
    q_comments = Comment.objects.filter(question=q)
    a_comments = Comment.objects.filter(answer__question=q)

    # Voting indicators
    if request.user.is_authenticated:
        vote_on_q = Vote.objects.filter(user=request.user, question=q)
        votes_on_answers = Vote.objects.filter(user=request.user,
                                               answer__in=q_answers)
        vote_on_best_answer = Vote.objects.filter(user=request.user,
                                                  answer_id=q_best_answer[0].id\
                                                      if len(q_best_answer)\
                                                      else -1)
        votes_on_q_comments = Vote.objects.filter(user=request.user,
                                                  comment__in=q_comments)
        votes_on_a_comments = Vote.objects.filter(user=request.user,
                                                  comment__in=a_comments)
        pos_vote_q = len(vote_on_q) and vote_on_q[0].positive
        neg_vote_q = len(vote_on_q) and not vote_on_q[0].positive

        pos_vote_a = [v.answer.id for v in list(votes_on_answers) \
                      + list(vote_on_best_answer) if v.positive]
        neg_vote_a = [v.answer.id for v in list(votes_on_answers) \
                      + list(vote_on_best_answer) if not v.positive]

        pos_vote_c = [v.comment.id for v in list(votes_on_a_comments) \
                      + list(votes_on_q_comments) if v.positive]
        neg_vote_c = [v.comment.id for v in list(votes_on_a_comments) \
                      + list(votes_on_q_comments) if not v.positive]
    else:
        pos_vote_a, pos_vote_c, pos_vote_q = [], [], False
        neg_vote_a, neg_vote_c, neg_vote_q = [], [], False

    # Increment the visits counter of the question by one
    if request.user.is_authenticated:
        q.visits += 1
        q.save()

    if len(q_best_answer) > 0:
        q_best_answer = q_best_answer.last()
    return render(request, 'qa_web/question_thread.html',
                  {'currentQuestion': q, 'answers': q_answers,
                   'bestAnswer': q_best_answer, 'q_comments': q_comments,
                   'a_comments': a_comments,
                   'initial_select_value': initial_select_value,
                   'pos_v_q': pos_vote_q, 'neg_v_q': neg_vote_q,
                   'pos_v_a': pos_vote_a, 'neg_v_a': neg_vote_a,
                   'pos_v_c': pos_vote_c, 'neg_v_c': neg_vote_c})


def vote(request):
    """Receives AJAX queries to vote on Posts, updates the corresponding Post
    and returns the new score.
    Should not be accessed directly, only in asynchronous queries.

    :param request: Request data provided by the WSGI
    :return: JSONResponse with the post's `new_score` and the post's score
            tag `id` in the DOM tree
    """
    if request.method == 'POST' and request.user.is_authenticated:
        vote_direction, button_id, post_type = request.POST['button'].split(
            '_')
        vote_direction = vote_direction == 'upvote'
        post_subclass = Question if post_type == 'question' else Answer \
            if post_type == 'answer' else Comment
        post = get_object_or_404(post_subclass, pk=int(button_id))
        # Workaround to provide the correct kwarg depending on post_type
        foreign_key_args = {post_type: post}
        if request.user not in post.voters.all():
            # Not yet voted on current post
            Vote.objects.create(user=request.user, positive=vote_direction,
                                **foreign_key_args)
            if vote_direction:
                post.upvotes = post.upvotes + 1
            else:
                post.downvotes = post.downvotes + 1
        else:
            # Modifying existing vote
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
        return JsonResponse({'new_score': post.score, 'id':
                             'score_{}_{}'.format(post.id, post_type)})
    # Accessing url without using Post or unauthenticated
    return HttpResponseRedirect('/')


def homepage(request):
    """Displays the website's home page.

    :param request: Request data provided by the WSGI
    :return: Rendered template displaying the home page
    """
    return render(request, "qa_web/home.html")


class QuestionDisplayView(ListView):
    """View for displaying the list of questions currently available."""
    model = Question
    paginate_by = 10
    context_object_name = 'questions'
    template_name = 'qa_web/question_index.html'
    ordering = '-creation_date'

    def get_context_data(self, *args, **kwargs):
        context = super(
            QuestionDisplayView, self).get_context_data(*args, **kwargs)

        context['total_question_num'] = Question.objects.count()
        context['total_answer_num'] = Answer.objects.count()

        # Try to page the question page
        # whether the paginator is needed. It's a must.
        context['is_paginated'] = True
        all_questions_qs = Question.objects.order_by('-creation_date') \
            .select_related('owner') \
            .annotate(num_answers=Count('answer', distinct=True),
                      num_question_comments=Count('comment', distinct=True),
                      num_tag=Count('tag', distinct=True))
        paginator_all_questions = Paginator(
            all_questions_qs, QuestionDisplayView.paginate_by)

        # Get question_page number from url
        page_0 = self.request.GET.get('question_page')
        try:
            page_obj = paginator_all_questions.page(page_0)

        except PageNotAnInteger:
            page_obj = paginator_all_questions.page(1)

        except EmptyPage:  # pragma: no cover
            page_obj = paginator_all_questions.page(
                paginator_all_questions.num_pages)
        context['latest_current_page'] = page_obj

        # Using modified paging num
        pagination_data = self._pagination_data(
            paginator_all_questions, page_obj, context['is_paginated'])
        context.update(pagination_data)

        # Pass tags to html.
        question_contenttype = ContentType.objects.get_for_model(Question)
        items = TaggedItem.objects.filter(content_type=question_contenttype)
        context['tags'] = Tag.objects.filter(
            taggit_taggeditem_items__in=items).exclude(
                slug__exact='').order_by('-id').distinct()

        return context

    def get_queryset(self):
        queryset = super(QuestionDisplayView, self).get_queryset() \
            .select_related('owner') \
            .annotate(num_answers=Count('answer', distinct=True),
                      num_question_comments=Count('comment', distinct=True))
        return queryset

    def _pagination_data(self, paginator, page, is_paginated):
        """to show page number like this:
        1...3 4 5- 6 7 ...9
        1...3 4 5- 6 7
        1 2 3-
        """
        if not is_paginated:
            # If no pagination, no more data needed.
            return {}

        pages_on_left = []
        pages_on_right = []
        ellipsis_on_left = False
        ellipsis_on_right = False
        display_first_page = False
        display_last_page = False

        page_number = page.number
        total_pages = paginator.num_pages
        page_range = paginator.page_range  # ex: [1, 2, 3, 4]

        if page_number == 1:
            # First page
            pages_on_right = page_range[page_number:page_number + 2]
            if len(pages_on_right) == 0:
                return {}

            if pages_on_right[-1] < total_pages - 1:
                ellipsis_on_right = True

            if pages_on_right[-1] < total_pages:
                display_last_page = True

        elif page_number == total_pages:
            # Last page
            pages_on_left = page_range[
                (page_number - 3) if (page_number - 3) > 0 else 0:
                page_number - 1]

            if len(pages_on_left) != 0 and pages_on_left[0] > 2:
                ellipsis_on_left = True

            if len(pages_on_left) != 0 and pages_on_left[0] > 1:
                display_first_page = True
        else:
            pages_on_left = page_range[
                (page_number - 3) if (page_number - 3) > 0 else 0:
                page_number - 1]
            pages_on_right = page_range[page_number:page_number + 2]

            if pages_on_right[-1] < total_pages - 1:
                ellipsis_on_right = True
            if pages_on_right[-1] < total_pages:
                display_last_page = True

        if len(pages_on_left) != 0 and pages_on_left[0] > 2:
            ellipsis_on_left = True
        if len(pages_on_left) != 0 and pages_on_left[0] > 1:
            display_first_page = True

        context = {
            'left': pages_on_left,
            'right': pages_on_right,
            'left_has_more': ellipsis_on_left,
            'right_has_more': ellipsis_on_right,
            'first': display_first_page,
            'last': display_last_page,
        }

        return context


class QuestionsByTagView(ListView):
    """View to call all the questions classified under one specific tag."""
    model = Question
    paginate_by = 10
    context_object_name = 'questions'
    template_name = 'qa_web/question_index.html'

    def get_queryset(self, **kwargs):
        return Question.objects.order_by('-creation_date').filter(
            tag__slug=self.kwargs['tag']) \
            .annotate(num_answers=Count('answer', distinct=True))

    def get_context_data(self, *args, **kwargs):
        context = super(QuestionsByTagView, self).get_context_data(
            *args, **kwargs)

        # Get default display objects from get_queryset.
        context['latest_current_page'] = context['questions']

        context['total_question_num'] = Question.objects.count()
        context['total_answer_num'] = Answer.objects.count()
        # Pass tags to html.
        question_contenttype = ContentType.objects.get_for_model(Question)
        items = TaggedItem.objects.filter(content_type=question_contenttype)
        context['tags'] = Tag.objects.filter(
            taggit_taggeditem_items__in=items).exclude(
                slug__exact='').order_by('-id').distinct()
        return context


@login_required(login_url='/login/')
def edit(request, id_):
    """Displays question editing form on a GET and modifies the question on a
    successful validation.
    Can only be accessed by the question's owner

    :param request: Request data provided by the WSGI
    :param id_: The question being edited's id
    :return: Rendered template displaying the form to edit a question on a GET
            or unsuccessful validation, else redirects to the question's
            answers page.
    """
    q = get_object_or_404(Question, pk=id_)
    if q.owner != request.user:
        return HttpResponseForbidden()

    form = EditForm(request.POST)
    if request.POST and form.is_valid():
        q.content = request.POST['content']
        q.title = request.POST['title']
        q.owner = request.user
        q.save()
        return HttpResponseRedirect('/questions/{q.id}/'.format(q=q))
    return render(request, 'qa_web/edit_post.html',
                  context={'post': q, 'is_answer': False})


@login_required(login_url='/login/')
def delete(request, id_):
    """Deletes a question and redirects to the question index
    Only the question's owner can delete it.

    :param request: Request data provided by the WSGI
    :param id_: The question's id
    :return: Redirects to the question index
    """
    q = get_object_or_404(Question, pk=id_)
    if q.owner != request.user:
        return HttpResponseForbidden()
    q.delete()
    return HttpResponseRedirect('/question_index/')


@login_required(login_url='/login/')
def edit_answers(request, id_, a_id):
    """Displays answer editing form on a GET and modifies the answer on a
    successful validation.
    Can only be accessed by the answer's owner

    :param request: Request data provided by the WSGI
    :param id_: The id of the question to which the answer belongs
    :param a_id: The id of the answer being edited
    :return: Rendered template displaying the form to edit an answer on a GET
            or unsuccessful validation, else redirects to the question's
            answers page.
    """
    a = get_object_or_404(Answer, pk=a_id)
    if a.owner != request.user:
        return HttpResponseForbidden()

    form = EditForm(request.POST)
    if request.POST and form.is_valid():
        a.content = request.POST['content']
        a.owner = request.user
        a.save()
        return HttpResponseRedirect('/questions/{id}/'.format(id=id_))
    return render(request, 'qa_web/edit_post.html',
                  context={'post': a, 'is_answer': True})


@csrf_exempt
def quick_search(request):
    if request.method == 'GET':
        keyword = request.GET['keyword']
        return HttpResponseRedirect('/search/?q=' + keyword)

