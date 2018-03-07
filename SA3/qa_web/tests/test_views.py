from datetime import date
from django.test import TestCase
from django.http import HttpResponseRedirect
from qa_web.models import User, Questions


credentials = {'username': 'test', 'password': 'test'}


class ViewTest(TestCase):
    """This class contains test methods for view functions"""

    def setUp(self):
        User.objects.create_user(**credentials)
    def _login(self):
        self.assertTrue(self.client.login(**credentials))

    def test_login(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        values = {
            'username' : credentials['username'],
            'password' : credentials['password'] + 'error'
        }
        response = self.client.post('/login/', data=values)
        self.assertContains(response, 'Incorrect username or password')

    def test_login_protected(self):
        """Pages that require a logged in user should redirect to the login page"""
        login_required_views = ['/questions/', '/editprofile/', '/questions/1/edit/']
        for url in login_required_views:
            response = self.client.get(url)
            self.assertRedirects(response, '/login/?next=' + url)

    def test_edit_profile(self):
        self._login()
        response = self.client.get('/editprofile/')
        self.assertEqual(response.status_code, 200)
        values = {
            'prename': 'Test',
            'surname': 'User',
            'age': '23',
            'birthday': '1960-01-01',
            'email': 'test@example.com',
            'motherland': 'Test',
            'school': 'Test',
            'major': 'Test',
            'city': 'Test'
        }
        response = self.client.post('/editprofile/', data=values)
        user = User.objects.get_by_natural_key(credentials['username'])
        self.assertRedirects(response, '/profile/{}/'.format(user.id))
        self.assertEqual(user.birthday, date(1960, 1, 1))
        self.assertEqual(user.email, values['email'])
        values['birthday'] = 'wrong format'
        response = self.client.post('/editprofile/', data=values)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid date.")

    def test_signup(self):

        get_response = self.client.get('/signup/')
        self.assertEqual(get_response.status_code, 200)
        form_entries = {
            'username' : 'NewUser',
            'password1' : 'password123',
            'password2' : 'password123'
        }
        response = self.client.post('/signup/', data=form_entries)
        self.assertRedirects(response, '/')
        self.assertTrue(User.objects.filter(username=form_entries['username']).exists())

    def test_asking_questions(self):
        response = self.client.get('/questions/')
        self.assertEqual(response.status_code, 302)
        form_data = {'title': 'test question',
                     'content': "test content",
                     'tag': 'testing'}

        response = self.client.post('/questions/', data= form_data)
        self.assertEqual(response.url, "/login/?next=/questions/")
        self._login()
        response = self.client.post('/questions/', data=form_data)
        last_question = Questions.objects.last()
        post_questions_count = Questions.objects.count()
        tags = last_question.tag.slugs()

        self.assertRedirects(response, '/questions/{}/'.format(last_question.id))
        self.assertEqual(post_questions_count, 1)
        self.assertEqual(tags[0], form_data['tag'])


class QuestionDisplayViewTest(TestCase):
    """This class contains test cases for the QuestionDisplayView"""

    def test_get_context(self):
        pass
