"""
Controller for Q&A website core features operations
involving post creation, edit or deletion
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.http import HttpResponseForbidden
from qa_web.forms import QuestionsForm, EditForm
from qa_web.models import Question, Answer


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
            question = Question(content=content, title=title, owner=owner)
            question.save()

            # Since a question can be submitted with no tag, filtering empty
            # and blank strings.
            for each_tag in tag:
                if each_tag.strip() != '':
                    question.tag.add(each_tag)

            return HttpResponseRedirect('/questions/{q.id}/'.format(q=question))
        else:
            return render(request, 'qa_web/posting_question.html', context={})


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
    question = get_object_or_404(Question, pk=id_)
    if question.owner != request.user:
        return HttpResponseForbidden()

    form = EditForm(request.POST)
    if request.POST and form.is_valid():
        question.content = request.POST['content']
        question.title = request.POST['title']
        question.owner = request.user
        question.save()
        return HttpResponseRedirect('/questions/{q.id}/'.format(q=question))
    return render(request, 'qa_web/edit_post.html',
                  context={'post': question, 'is_answer': False})


@login_required(login_url='/login/')
def delete(request, id_):
    """Deletes a question and redirects to the question index
    Only the question's owner can delete it.

    :param request: Request data provided by the WSGI
    :param id_: The question's id
    :return: Redirects to the question index
    """
    question = get_object_or_404(Question, pk=id_)
    if question.owner != request.user:
        return HttpResponseForbidden()
    question.delete()
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
    answer = get_object_or_404(Answer, pk=a_id)
    if answer.owner != request.user:
        return HttpResponseForbidden()

    form = EditForm(request.POST)
    if request.POST and form.is_valid():
        answer.content = request.POST['content']
        answer.owner = request.user
        answer.save()
        return HttpResponseRedirect('/questions/{id}/'.format(id=id_))
    return render(request, 'qa_web/edit_post.html',
                  context={'post': answer, 'is_answer': True})
