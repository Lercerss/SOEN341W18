from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from qa_web.forms import UserProfile
from qa_web.models import Answer, Comment, Question, User


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
        form = UserProfile(initial=existing_data)
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
    user_comments = Comment.objects.filter(owner_id=id_)
    return render(request, 'qa_web/user_profile.html',
                  context={'displayed_user': displayed_user,
                           'questions': user_questions,
                           'answers': user_answers,
                           'comments': user_comments})
