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
