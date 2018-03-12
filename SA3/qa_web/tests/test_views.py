import re
from datetime import date
from django.test import TestCase
from django.http import HttpResponseRedirect
from qa_web.models import User, Questions, Answers, Comments
from qa_web.views import QuestionDisplayView, QuestionsByTagView


credentials = {'username': 'test', 'password': 'test'}

def _populate_db(user, num_answers, comments_per_answer):
        q = Questions.objects.create(title="Test question", content="Test content", owner=user)
        for i in range(num_answers):
            a = Answers.objects.create(content="answer content " + str(i), owner=user, question=q)
            for j in range(comments_per_answer):
                Comments.objects.create(content="comment content {}-{}".format(i, j), owner=user, answer=a)

        return q

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

    def test_answers_simple(self):
        user = User.objects.get(pk=1)
        num_answers, comments_per_answer = 10, 3
        q = _populate_db(user, num_answers, comments_per_answer)
        response = self.client.get('/questions/{}/'.format(q.id))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0 visits") # Only authenticated users increment the view counter
        self.assertEqual(response.context['currentQuestion'], q)
        # Matches score items to count number of posts displayed on the page
        matches = re.findall(r'score_\d+_(answer|comment|question)', response.content.decode())
        self.assertEqual(len(matches), num_answers*comments_per_answer + num_answers + 1)
        self.assertNotContains(response, 'Be the first to answer this question!')
        self.assertFalse(response.context['bestAnswer'])
    
    def test_answers_select_best(self):
        user = User.objects.get(pk=1)
        num_answers = 3
        q = _populate_db(user, num_answers, 0)
        values = {
            'select_{}'.format(Answers.objects.filter(question=q)[0].id): 'Select as Best Answer'
        }
        response = self.client.post('/questions/{}/'.format(q.id), data=values)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'good_answer')
        response = self.client.post('/questions/{}/'.format(q.id), data={'deselect': 'Deselect as Best Answer'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'good_answer')

    def test_answers_add_answer(self):
        user = User.objects.get(pk=1)
        num_answers = 3
        q = _populate_db(user, num_answers, 0)
        self._login()
        values = {
            'answer_form': '',
            'content': 'Some content'
        }
        response = self.client.post('/questions/{}/'.format(q.id), data=values)
        self.assertEqual(response.status_code, 200)
        matches = re.findall(r'score_\d+_answer', response.content.decode())
        self.assertEqual(len(matches), num_answers + 1)

    def test_answers_add_comment(self):
        user = User.objects.get(pk=1)
        num_answers, comments_per_answer = 3, 3
        q = _populate_db(user, num_answers, comments_per_answer)
        self._login()
        values = {
            'comment_form_answer_{}'.format(Answers.objects.filter(question=q)[0].id): '',
            'content': 'Some content'
        }
        response = self.client.post('/questions/{}/'.format(q.id), data=values)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comments.objects.count(), num_answers * comments_per_answer + 1)

    def test_answers_view_count(self):
        user = User.objects.get(pk=1)
        q = _populate_db(user, 1, 1)
        self._login()
        amount = 10
        for i in range(amount):
            response = self.client.get('/questions/{}/'.format(q.id))

        self.assertContains(response, '{} visits'.format(amount))

    def test_vote_question(self):
        user = User.objects.get(pk=1)
        q = _populate_db(user, 1, 1)
        self._login()
        values = {
            'button': 'upvote_{}_question'.format(q.id)
        }
        response = self.client.post('/vote/', data=values)
        self.assertEqual(response.json(), {'id':'score_{}_question'.format(q.id), 'new_score': 1})

    def test_vote_answer(self):
        user = User.objects.get(pk=1)
        q = _populate_db(user, 1, 1)
        a = Answers.objects.get(question=q)
        self._login()
        values = {
            'button': 'upvote_{}_answer'.format(a.id)
        }
        response = self.client.post('/vote/', data=values)
        self.assertEqual(response.json(), {'id':'score_{}_answer'.format(a.id), 'new_score': 1})

    def test_vote_comment(self):
        user = User.objects.get(pk=1)
        q = _populate_db(user, 1, 1)
        c = Comments.objects.all()[0]
        self._login()
        values = {
            'button': 'upvote_{}_comment'.format(c.id)
        }
        response = self.client.post('/vote/', data=values)
        self.assertEqual(response.json(), {'id':'score_{}_comment'.format(q.id), 'new_score': 1})

    def test_vote_no_ajax(self):
        self._login()
        response = self.client.get('/vote/')
        self.assertRedirects(response, '/')

    def test_edit_profile(self):
        self._login()
        q = _populate_db(User.objects.get(pk=1), 1, 1)
        values = {
            'content': 'New content displayed! {}'.format(hash(q)),
            'title': 'A new title! {}'.format(hash(q)) 
        }
        response = self.client.post('/questions/{}/edit/'.format(q.id), data=values)
        self.assertRedirects(response, '/questions/{}/'.format(q.id))
        self.assertEqual(Questions.objects.get(pk=q.id).content, values['content'])
        self.assertEqual(Questions.objects.get(pk=q.id).title, values['title'])

    def test_edit_profile_forbidden(self):
        other_user = User.objects.create_user(username='other_user', password='wat')
        self._login()
        q = _populate_db(other_user, 1, 1)
        response = self.client.get('/questions/{}/edit/'.format(q.id))
        self.assertEqual(response.status_code, 403) # Forbidden since other_user owns q


class QuestionDisplayViewTest(TestCase):
    """This class contains test cases for the QuestionDisplayView"""

    def setUp(self):
        User.objects.create_user(**credentials)

    def test_pagination(self):
        user = User.objects.get(pk=1)
        questions = []
        num_questions, num_answers, comments_per_answer = 50, 10, 3
        for i in range(num_questions):
            questions.append(_populate_db(user, num_answers, comments_per_answer))

        response = self.client.get('/QuestionIndex/')
        self.assertEqual(len(response.context['latest_current_page']), QuestionDisplayView.paginate_by)
        self.assertEqual(response.context['left'], [])
        self.assertEqual(response.context['right'], range(2,4)) # [2, 3]
        self.assertEqual(response.context['latest_current_page'].number, 1)

        response = self.client.get('/QuestionIndex/', data={'question_page': 3})
        self.assertEqual(len(response.context['latest_current_page']), QuestionDisplayView.paginate_by)
        self.assertEqual(response.context['left'], range(1,3))
        self.assertEqual(response.context['right'], range(4,6))
        self.assertEqual(response.context['latest_current_page'].number, 3)


class QuestionsByTagViewTest(TestCase):
    """Test cases for QuestionByTagView"""
    
    def setUp(self):
        User.objects.create_user(**credentials)
    
    def test_tagview(self):
        user = User.objects.get(pk=1)
        for i in range(10):
            _populate_db(user, 1, 1)

        for i, q in enumerate(Questions.objects.all()):
            q.tag.add('test')
            if i % 3 == 0: # 0, 3, 6, 9...
                q.tag.add('other')
            q.save()

        response = self.client.get('/tag/other/')
        self.assertEqual(len(response.context['latest_current_page']), 4)
        response = self.client.get('/tag/test/')
        self.assertEqual(len(response.context['latest_current_page']), 10)