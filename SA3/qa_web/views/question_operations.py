"""
Controller for Q&A website additional features operations
"""

from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from django.http import JsonResponse
from django.db.models import Count, F
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from taggit.models import Tag, TaggedItem
from qa_web.models import Answer, Comment, Question, Vote
from qa_web.forms import AnswersForm

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
    question = get_object_or_404(Question, pk=id_)
    answer_id = [int(key.replace('select_', ''))
                 for key in request.POST.keys() if key.startswith('select_')]
    if request.method == 'POST' and 'answer_form' in request.POST:
        # Answering a question
        form = AnswersForm(request.POST)
        if form.is_valid():
            Answer.objects.create(
                content=request.POST['content'], owner=request.user,
                question=question)

    elif request.method == 'POST' and 'deselect' in request.POST and \
            question.owner.id == request.user.id:
        # Deselecting best answer
        update_answer = Answer.objects.filter(
            question=question, correct_answer=True).last()
        update_answer.correct_answer = False
        update_answer.save()
    elif answer_id and question.owner.id == request.user.id:
        # Selecting best answer
        update_answer = Answer.objects.get(id=answer_id[0])
        update_answer.correct_answer = True
        update_answer.save()
    elif any(key.startswith("comment_form_answer") for key in request.POST.keys()):
        # Commenting on an answer
        answer_id = [int(key.replace('comment_form_answer_', '')) for key
                     in request.POST.keys() if key.startswith('comment_form')]
        answer = Answer.objects.get(id=answer_id[0])
        comment = Comment(content=request.POST['content'],
                          owner=request.user, answer=answer)
        comment.save()
    elif request.method == 'POST' and 'comment_form_question' in request.POST:
        # Commenting on the question
        comment = Comment(content=request.POST['content'],
                          owner=request.user, question=question)
        comment.save()

    # Ordering answers
    if request.method == 'POST' and 'sort_by_form_select' in request.POST:
        initial_select_value = request.POST['sort_by_form_select']
        if request.POST['sort_by_form_select'] == 'lowestScore':
            q_answers = Answer.objects.filter(question=question,
                                              correct_answer=False)\
                .annotate(points=F('upvotes') - F('downvotes'))\
                .order_by('points')
        elif request.POST['sort_by_form_select'] == 'highestScore':
            q_answers = Answer.objects.filter(question=question,
                                              correct_answer=False)\
                .annotate(points=F('upvotes') - F('downvotes'))\
                .order_by('-points')
        elif request.POST['sort_by_form_select'] == 'leastRecent':
            q_answers = Answer.objects.filter(
                question=question, correct_answer=False) \
                .order_by('creation_date')
        else:  # Most Recent
            q_answers = Answer.objects.filter(
                question=question, correct_answer=False) \
                .order_by('-creation_date')
    else:
        initial_select_value = "highestScore"
        q_answers = Answer.objects.filter(question=question,
                                          correct_answer=False)\
            .annotate(points=F('upvotes') - F('downvotes')).order_by('-points')

    q_best_answer = Answer.objects.filter(question=question,
                                          correct_answer=True)
    q_comments = Comment.objects.filter(question=question)
    a_comments = Comment.objects.filter(answer__question=question)

    # Voting indicators
    if request.user.is_authenticated:
        vote_on_q = Vote.objects.filter(user=request.user, question=question)
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
        question.visits += 1
        question.save()

    if len(q_best_answer) > 0:
        q_best_answer = q_best_answer.last()
    return render(request, 'qa_web/question_thread.html',
                  {'currentQuestion': question, 'answers': q_answers,
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

@csrf_exempt
def quick_search(request):
    if request.method == 'GET':
        keyword = request.GET['keyword']
        return HttpResponseRedirect('/search/?q=' + keyword)
