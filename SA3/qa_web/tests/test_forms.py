from django.test import TestCase
from qa_web.models import User
from qa_web.forms import UserProfile, QuestionsForm, AnswersForm, LoginForm, EditForm

credentials = {'username': 'test', 'password': 'test'}

# Create your tests here.
class FormTest(TestCase):

    def setUp(self):
        User.objects.create_user(**credentials)

    def test_user_profile(self):
        form_data = {'prename': 'John',
                     'surname': 'Smith',
                     'email': 'test@example.com',
                     'age': '40',
                     'birthday': '1960-08-24',
                     'motherland': 'le quebec',
                     'school': 'McGill University',
                     'major': 'COMP SCI',
                     'city': 'Montreal'}
        form = UserProfile(data=form_data)
        self.assertTrue(form.is_valid())

        invalid_dates= ['1960-08-32', '1960/08/24', '2030-08-32', '1960-24-08']

        for date in invalid_dates:
            form_data['birthday'] = date
            form = UserProfile(data=form_data)
            self.assertJSONEqual(form.errors.as_json(),
                                 {"birthday": [{"code": "invalid", "message": "Enter a valid date."}]})


    def test_question(self):

        form_data = { 'title': 'How do we query from views content from models in Django?',
                      'content':"When I try to query from `models.py` using filter, I **cannot** access the \
                                element's attribute. Why is this?"}
        form = QuestionsForm(data = form_data)
        self.assertTrue(form.is_valid())

    def test_answer(self):
        form_data = { 'content': "Test content for an answer"}

        form = AnswersForm(data= form_data)
        self.assertTrue(form.is_valid())

    def test_edit(self):

        form_data = { 'content': "Test content for editing a question"}
        form = EditForm(data= form_data)
        self.assertTrue(form.is_valid())

    def test_login(self):

        form_data = {'username': None, 'password': None}
        login = LoginForm(data = form_data)
        self.assertFalse(login.is_valid())
        self.assertJSONEqual(login.errors.as_json(), {"password": [{"message": "please input password", "code": "required"}],
                                                  "__all__": [{"message": "username and password are required", "code": ""}],
                                                  "username": [{"message": "please input username", "code": "required"}]})

