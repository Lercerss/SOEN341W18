__author__ = 'jet'

from django import forms


class LoginForm(forms.Form):
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
            cleaned_data = super(LoginForm, self).clean()


class Questions(forms.Form):
    title = forms.CharField(
        required=True,
        label='title',
        error_messages={'required': u'please submit a question'},
    )



class Answers(forms.Form):
    title = forms.CharField(
        required=True,
        label='title',
        error_messages={'required': u'please submit a question'},
    )

