"""Forms used in the qa_web app.
For more information: https://docs.djangoproject.com/en/2.0/topics/forms/
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from qa_web.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields


class LoginForm(forms.Form):
    """Form used to login a user to the website"""
    username = forms.CharField(
        required=True,
        label='username',
        error_messages={'required': 'please input username'},

    )
    password = forms.CharField(
        required=True,
        label='password',
        error_messages={'required': u'please input password'},
    )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("username and password are required")
        else:
            self.cleaned_data = super(LoginForm, self).clean()


class QuestionsForm(forms.Form):
    """Form used to create a question"""
    title = forms.CharField(
        required=True,
        label='title',
        error_messages={'required': 'please input question title'},
    )

    content = forms.Textarea()


class AnswersForm(forms.Form):
    """Form used to add an answer to a question"""
    content = forms.Textarea()


class UserProfile(forms.Form):
    """Form used to modify user profile information"""
    prename = forms.CharField(
        required=True,
        label='Prename',
        error_messages={'required': 'Please insert your first name.'},

    )

    surname = forms.CharField(
        required=True,
        label='Surname',
        error_messages={'required': 'Please insert your last name.'},

    )

    email = forms.CharField(
        required=True,
        label='E-Mail:',
        error_messages={'required': 'Please insert your last e-mail.'},

    )
    age = forms.IntegerField(
        required=True,
        label='Age',
        error_messages={'required': 'Please insert an age.'},

    )

    birthday = forms.DateField(
        required=True,
        label='Birthday (YYYY-MM-DD)',
        error_messages={'required':
                        'Please insert birthday in the format of (yyyy-mm-dd)'}
    )

    motherland = forms.CharField(
        required=True,
        label="Motherland",
        error_messages={
            'required': 'Please insert the country of your native land'},
    )

    school = forms.CharField(
        required=True,
        label="School",
        error_messages={'required': 'Please insert the name of your school'},
    )

    major = forms.CharField(
        required=True,
        label="Major",
        error_messages={'required': 
        'Please insert your main subject of studies. Ex: Software Engineering'}
    )

    city = forms.CharField(
        required=True,
        label="city",
        error_messages={
            'required': 'Please insert the name of your current city'},
    )


class EditForm(forms.Form):
    """Form used to edit a question"""
    content = forms.Textarea()
