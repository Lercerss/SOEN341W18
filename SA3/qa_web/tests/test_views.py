"""
Submodule that defines test cases to be ran for views
"""

import re
from datetime import date
from django.test import TestCase
from qa_web.models import User, Question, Answer, Comment
from qa_web.views import QuestionDisplayView

credentials = {'username': 'test', 'password': 'test'}


def _populate_db(user, num_answers, comments_per_answer):
    """
    Helper function that populates test database with a question containing
    questions, answers and comments for a specific user
    :param user: User object
    :param num_answers: number of fake answers
    :param comments_per_answer: number of fake comments per answer
    :return: Question object created
    """
    question = Question.objects.create(
        title="Test question", content="Test content", owner=user)
    for i in range(num_answers):
        answer = Answer.objects.create(
            content="answer content " + str(i), owner=user, question=question)
        for j in range(comments_per_answer):
            Comment.objects.create(
                content="comment content {}-{}".format(i, j),
                owner=user, answer=answer)

    return question


class ViewTest(TestCase):
    """This class contains test methods for view functions"""

    def setUp(self):
        """
        Method that sets up the test case environment for
        testing of qa_web core functionalities
        """
        User.objects.create_user(**credentials)

    def _login(self):
        """
        Helper method that logs in the user with global credentials
        """
        self.assertTrue(self.client.login(**credentials))

    def test_login(self):
        """
        Tests the login functionality
        """
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        values = {
            'username': credentials['username'],
            'password': credentials['password'] + 'error'
        }
        response = self.client.post('/login/', data=values)
        self.assertContains(response, 'Incorrect username or password')
        values['password'] = ''
        response = self.client.post('/login/', data=values)
        self.assertEqual(response.status_code, 200)
        values['password'] = credentials['password']
        response = self.client.post('/login/', data=values)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_logout(self):
        """
        Tests the log out functionality
        """
        self._login()
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/')
        self.assertEqual(response.status_code, 302)

    def test_login_protected(self):
        """
        Pages that require a logged in user should redirect to the
        login page
        """
        login_required_views = ['/questions/',
                                '/edit_profile/', '/questions/1/edit/']
        for url in login_required_views:
            response = self.client.get(url)
            self.assertRedirects(response, '/login/?next=' + url)

    def test_editing_profile(self):
        """
        Tests the opening of edit user profile page
        and the submission of an edited user profile
        """
        self._login()
        response = self.client.get('/edit_profile/')
        self.assertEqual(response.status_code, 200)
        values = {
            'prename': 'Test',
            'surname': 'User',
            'email': 'test@example.com',
            'age': '23',
            'birthday': '1960-01-01',
            'motherland': 'Test',
            'school': 'Test',
            'major': 'Test',
            'city': 'Test'
        }
        response = self.client.post('/edit_profile/', data=values)
        user = User.objects.get_by_natural_key(credentials['username'])
        self.assertRedirects(response, '/profile/{}/'.format(user.id))
        self.assertEqual(user.birthday, date(1960, 1, 1))
        self.assertEqual(user.email, values['email'])
        values['birthday'] = 'wrong format'
        response = self.client.post('/edit_profile/', data=values)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid date.")

    def test_displaying_profile(self):
        """
        Tests the opening of a user profile page
        """
        self._login()
        user = User.objects.get_by_natural_key(credentials['username'])
        num_answers, comments_per_answer = 5, 2
        question = _populate_db(user, num_answers, comments_per_answer)
        comment = Comment(content="test", question=question, owner=user)
        comment.save()

        self.assertIsNotNone(question)
        response = self.client.get('/profile/{}/'.format(user.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['answers'].count(), num_answers)
        self.assertEqual(response.context['questions'].count(), 1)

    def test_signup(self):
        """
        Tests the opening of the sign up page and the submission
        of a new sign up form
        """
        get_response = self.client.get('/signup/')
        self.assertEqual(get_response.status_code, 200)
        form_entries = {
            'username': 'NewUser',
            'password1': 'password123',
            'password2': 'password123'
        }
        response = self.client.post('/signup/', data=form_entries)
        self.assertRedirects(response, '/')
        self.assertTrue(User.objects.filter(
            username=form_entries['username']).exists())

    def test_asking_questions(self):
        """
        Tests the process of asking a new question
        """
        response = self.client.get('/questions/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/questions/')

        form_data = {
            'title': 'test question',
            'content': "test content",
            'tag': 'testing'
        }
        response = self.client.post('/questions/', data=form_data)
        self.assertEqual(response.url, "/login/?next=/questions/")
        self._login()
        response = self.client.get('/questions/')
        self.assertTemplateUsed(response, 'qa_web/posting_question.html')
        response = self.client.post('/questions/', data=form_data)
        last_question = Question.objects.last()
        post_questions_count = Question.objects.count()
        tags = last_question.tag.slugs()

        self.assertRedirects(
            response, '/questions/{}/'.format(last_question.id))
        self.assertEqual(post_questions_count, 1)
        self.assertEqual(tags[0], form_data['tag'])

        form_data = {'wrong': 'form'}
        response = self.client.post('/questions/', data=form_data)
        self.assertTemplateUsed(response, 'qa_web/posting_question.html')

    def test_answers_simple(self):
        """
        Tests the display of answers and comments on questions page
        """
        user = User.objects.get(pk=1)
        num_answers, comments_per_answer = 10, 3
        question = _populate_db(user, num_answers, comments_per_answer)
        response = self.client.get('/questions/{}/'.format(question.id))
        self.assertEqual(response.status_code, 200)
        # Only authenticated users increment the view counter
        self.assertContains(response, "0 visits")
        self.assertEqual(response.context['currentQuestion'], question)
        # Matches score items to count number of posts displayed on the page
        matches = re.findall(
            r'score_\d+_(answer|comment|question)', response.content.decode())
        self.assertEqual(len(matches), num_answers *
                         comments_per_answer + num_answers + 1)
        self.assertNotContains(
            response, 'Be the first to answer this question!')
        self.assertFalse(response.context['bestAnswer'])

    def test_answers_select_best(self):
        """
        Tests the process of selecting and deselecting a best answer
        to a question
        """
        user = User.objects.get(pk=1)
        num_answers = 3
        question = _populate_db(user, num_answers, 0)
        key = 'select_{}'.format(Answer.objects.filter(question=question)[0].id)
        values = {
            key: 'Select as Best Answer'
        }
        response = self.client.post('/questions/{}/'.format(question.id),
                                    data=values)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'good-answer')
        self._login()
        response = self.client.post('/questions/{}/'.format(question.id),
                                    data=values)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'good-answer')
        response = self.client.post('/questions/{}/'.format(question.id),
                                    data={'deselect': 'Deselect as Best Answer'
                                         })
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'good-answer')

    def test_answers_add_answer(self):
        """
        Tests the process of posting an answer
        """
        user = User.objects.get(pk=1)
        num_answers = 3
        question = _populate_db(user, num_answers, 0)
        self._login()
        values = {
            'answer_form': '',
            'content': 'Some content'
        }
        response = self.client.post('/questions/{}/'.format(question.id),
                                    data=values)
        self.assertEqual(response.status_code, 200)
        matches = re.findall(r'score_\d+_answer', response.content.decode())
        self.assertEqual(len(matches), num_answers + 1)

    def test_answers_add_comment(self):
        """
        Tests the process of adding a comment to an answer
        """
        user = User.objects.get(pk=1)
        num_answers, comments_per_answer = 3, 3
        question = _populate_db(user, num_answers, comments_per_answer)
        self._login()
        key = 'comment_form_answer_{}'.format(
            Answer.objects.filter(question=question)[0].id)
        values = {
            key: '',
            'content': 'Some content'
        }
        response = self.client.post('/questions/{}/'.format(question.id),
                                    data=values)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(),
                         num_answers * comments_per_answer + 1)

    def test_questions_view_count(self):
        """
        Tests the view count feature for a certain question
        """
        user = User.objects.get(pk=1)
        question = _populate_db(user, 1, 1)
        self._login()
        amount = 10
        for i in range(amount):
            response = self.client.get('/questions/{}/'.format(question.id))

        self.assertContains(response, '{} visits'.format(amount))

    def test_ordering_answers(self):
        """
        Tests the process of ordering answers on the question page.
        All possibilities of sorting are tested
        """
        user = User.objects.get(pk=1)
        question = _populate_db(user, 1, 1)
        self.assertIsNotNone(question)
        response = self.client.get('/questions/{}/'.format(question.id))
        self.assertEqual(response.status_code, 200)

        options = ['highestScore', 'lowestScore', 'mostRecent', 'leastRecent']

        for ordering in options:
            context = {
                'sort_by_form_select': ordering
            }
            self.client.post('/questions/{}/'.format(question.id), data=context)
            self.assertEqual(response.status_code, 200)

        context = {
            'sort_by_form_select_same': 'useless'
        }
        self.client.post('/questions/{}/'.format(question.id), data=context)
        self.assertEqual(response.status_code, 200)

    def test_vote_question(self):
        """
        Tests the process of voting for a question
        """
        user = User.objects.get(pk=1)
        question = _populate_db(user, 1, 1)
        self._login()
        values = {
            'button': 'upvote_{}_question'.format(question.id)
        }
        response = self.client.post('/vote/', data=values)
        self.assertEqual(response.json(), {
            'id': 'score_{}_question'.format(question.id), 'new_score': 1})

    def test_vote_answer(self):
        """
        Tests in an exhaustive manner the voting possibilites for
        a certain answer
        :return:
        """
        user = User.objects.get(pk=1)
        question = _populate_db(user, 1, 1)
        answer = Answer.objects.get(question=question)
        self._login()

        values = {
            'button': 'downvote_{}_answer'.format(answer.id)
        }
        response = self.client.post('/vote/', data=values)  # downvote
        self.assertEqual(response.json(), {
            'id': 'score_{}_answer'.format(answer.id), 'new_score': -1})
        response = self.client.post('/vote/', data=values)  # cancel downvote
        self.assertEqual(response.json(), {
            'id': 'score_{}_answer'.format(answer.id), 'new_score': 0})
        values['button'] = 'upvote_{}_answer'.format(answer.id)
        response = self.client.post('/vote/', data=values)  # upvote
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'id': 'score_{}_answer'.format(answer.id), 'new_score': +1})
        response = self.client.post('/vote/', data=values)  # cancel upvote
        self.assertEqual(response.json(), {
            'id': 'score_{}_answer'.format(answer.id), 'new_score': 0})
        self.client.post('/vote/', data=values)  # back to +1
        values['button'] = 'downvote_{}_answer'.format(answer.id)
        # override upvote with downvote
        response = self.client.post('/vote/', data=values)
        self.assertEqual(response.json(), {
            'id': 'score_{}_answer'.format(answer.id), 'new_score': -1})
        values['button'] = 'upvote_{}_answer'.format(answer.id)
        # override downvote with upvote
        response = self.client.post('/vote/', data=values)
        self.assertEqual(response.json(), {
            'id': 'score_{}_answer'.format(answer.id), 'new_score': +1})

    def test_vote_comment(self):
        """
        Tests the process of voting on a comment
        """
        user = User.objects.get(pk=1)
        question = _populate_db(user, 1, 1)
        comment = Comment.objects.all()[0]
        self._login()
        values = {
            'button': 'upvote_{}_comment'.format(comment.id)
        }
        response = self.client.post('/vote/', data=values)
        self.assertEqual(response.json(), {
            'id': 'score_{}_comment'.format(question.id), 'new_score': 1})

    def test_question_comment(self):
        """
        Tests the process of posting a comment for a
        certain question
        """
        user = User.objects.get(pk=1)
        question = _populate_db(user, 1, 1)

        self._login()
        values = {
            'content': 'Test comment',
            'comment_form_question': ['Submit your comment']
        }
        response = self.client.post('/questions/{}/'.format(question.id),
                                    data=values)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, values['content'])

    def test_vote_no_ajax(self):
        """
        Tests the non-ajax vote request
        """
        self._login()
        response = self.client.get('/vote/')
        self.assertRedirects(response, '/')

    def test_edit_questions(self):
        """
        Tests the process of editing a question
        """
        self._login()
        question = _populate_db(User.objects.get(pk=1), 1, 1)
        response = self.client.get('/questions/{}/edit/'.format(question.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'qa_web/edit_post.html')
        values = {
            'content': 'New content displayed! {}'.format(hash(question)),
            'title': 'A new title! {}'.format(hash(question))
        }
        response = self.client.post(
            '/questions/{}/edit/'.format(question.id), data=values)
        self.assertRedirects(response, '/questions/{}/'.format(question.id))
        self.assertEqual(Question.objects.get(
            pk=question.id).content, values['content'])
        self.assertEqual(Question.objects.get(pk=question.id).title,
                         values['title'])

    def test_edit_profile_forbidden(self):
        """
        Tests the attempt to edit a profile under incorrect user
        """
        other_user = User.objects.create_user(
            username='other_user', password='wat')
        self._login()
        question = _populate_db(other_user, 1, 1)
        response = self.client.get('/questions/{}/edit/'.format(question.id))
        # Forbidden since other_user owns q
        self.assertEqual(response.status_code, 403)

    def test_delete_post(self):
        """
        Tests the process of questions deletion
        """
        other_user = User.objects.create_user(
            username='other_user', password='wat')
        self._login()
        question = _populate_db(other_user, 1, 1)
        response = self.client.get('/questions/{}/delete/'.format(question.id))
        self.assertEqual(response.status_code, 403)
        question.delete()
        question = _populate_db(User.objects.get(pk=1), 1, 1)
        response = self.client.get('/questions/{}/delete/'.format(question.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(Answer.objects.count(), 0)

    def test_edit_answers(self):
        """
        Tests the process of editing an answer
        """
        other_user = User.objects.create_user(
            username='other_user', password='wat')
        self._login()
        question = _populate_db(other_user, 1, 1)
        answer = Answer.objects.get(question=question)
        response = self.client.get(
            '/questions/{}/edit_answers/{}/'.format(question.id, answer.id))
        self.assertEqual(response.status_code, 403)
        question.delete()
        answer.delete()
        self._login()
        question = _populate_db(User.objects.get(pk=1), 1, 1)
        answer = Answer.objects.get(question=question)
        response = self.client.get(
            '/questions/{}/edit_answers/{}/'.format(question.id, answer.id))
        self.assertEqual(response.status_code, 200)
        values = {
            'content': 'New content displayed!'
        }
        self.client.post(
            '/questions/{}/edit_answers/{}/'.format(question.id, answer.id),
            data=values)
        self.assertEqual(Answer.objects.get(
            pk=answer.id).content, values['content'])

    def test_quick_search(self):
        """
        Tests and simulates a quick search on the navbar
        """
        form_entries = {
            'keyword': 'python'
        }
        get_response = self.client.get('/quick_search/', data=form_entries)
        self.assertEqual(get_response.status_code, 302)


class QuestionDisplayViewTest(TestCase):
    """This class contains test cases for the QuestionDisplayView"""

    def setUp(self):
        """
        Method that sets up the test case environment for
        testing of questions display page
        """
        User.objects.create_user(**credentials)

    def test_pagination(self):
        """
        Tests the display of multiple questions and
        its resulting pagination
        """
        user = User.objects.get(pk=1)
        response = self.client.get('/question_index/')
        self.assertEqual(response.status_code, 200)

        questions = []
        num_questions, num_answers, comments_per_answer = 50, 10, 3
        for i in range(num_questions):
            questions.append(_populate_db(
                user, num_answers, comments_per_answer))

        response = self.client.get('/question_index/')
        self.assertEqual(len(response.context['latest_current_page']),
                         QuestionDisplayView.paginate_by)
        self.assertEqual(response.context['left'], [])
        self.assertEqual(response.context['right'], range(2, 4))  # [2, 3]
        self.assertEqual(response.context['latest_current_page'].number, 1)

        response = self.client.get(
            '/question_index/', data={'question_page': 3})
        self.assertEqual(len(response.context['latest_current_page']),
                         QuestionDisplayView.paginate_by)
        self.assertEqual(response.context['left'], range(1, 3))
        self.assertEqual(response.context['right'], range(4, 6))
        self.assertEqual(response.context['latest_current_page'].number, 3)

        response = self.client.get(
            '/question_index/', data={'question_page': 5})
        self.assertEqual(response.status_code, 200)


class QuestionsByTagViewTest(TestCase):
    """Test cases for QuestionByTagView"""

    def setUp(self):
        """
        Method that sets up the test case environment for
        testing of tagging system
        """
        User.objects.create_user(**credentials)

    def test_tagview(self):
        """
        Tests the filtering of questions by tags
        """
        user = User.objects.get(pk=1)
        for i in range(10):
            _populate_db(user, 1, 1)

        for i, question in enumerate(Question.objects.all()):
            question.tag.add('test')
            if i % 3 == 0:  # 0, 3, 6, 9...
                question.tag.add('other')
            question.save()

        response = self.client.get('/tag/other/')
        self.assertEqual(len(response.context['latest_current_page']), 4)
        response = self.client.get('/tag/test/')
        self.assertEqual(len(response.context['latest_current_page']), 10)
