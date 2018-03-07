from django.test import TestCase
from qa_web.forms import UserProfile, QuestionsForm


# Create your tests here.
class FormTest(TestCase):

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

    def test_question(self):

        form_data = { 'title': 'How do we query from views content from models in Django?',
                      'content':"When I try to query from `models.py` using filter, I **cannot** access the \
                                element's attribute. Why is this?"}
        form =  QuestionsForm(data = form_data)
        self.assertTrue(form.is_valid())