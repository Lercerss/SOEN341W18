from django.test import TestCase
from qa_web.forms import UserProfile


# Create your tests here.
class FormTest(TestCase):

    def test_user_profile(self):
        form_data = {'prename': 'John', 'surname': 'Smith',
                     'email': 'test@example.com', 'age': '40', 'birthday': '1960-08-24',
                     'motherland': 'le quebec', 'school': 'McGill University',
                     'major': 'COMP SCI', 'city': 'Montreal'}
        form = UserProfile(data=form_data)
        self.assertTrue(form.is_valid())
