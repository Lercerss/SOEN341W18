from django.test import TestCase
from django.contrib.auth import authenticate
from qa_web.models import Question, Comment, Answer, User, Vote
import random

credentials = {'username': 'johnny', 'password': 'password123'}


def obtain_sample_objects_as_tuple():
    user1 = User.objects.first()
    q = Question.objects.first()
    a = Answer.objects.first()
    return user1, q, a


def create_many_users():
    for i in range(0, 15):
        name = 'User{}'.format(i)
        pw = str(i)
        u = User.objects.create(username=name, password=pw)
    return


class CommentModel(TestCase):
    """Test cases for Comment model"""

    def setUp(self):
        user1 = User.objects.create_user(**credentials)
        title = "What is life?"
        content = "Someone please explain to me the purpose of life"
        Question.objects.create(title=title, content=content, owner=user1)
        Answer.objects.create(
            content='Test answer', owner=user1, correct_answer=True)

    def test_to_string_method_question(self):
        _, q, _ = obtain_sample_objects_as_tuple()
        self.assertEqual(str(q), q.title)

    def test_get_answer_queryset(self):
        _, q, a = obtain_sample_objects_as_tuple()
        self.assertEqual(None, q.get_answer_queryset().first())

    def test_question_comment_instantiation(self):
        user1, q, _ = obtain_sample_objects_as_tuple()

        c = Comment.objects.create(content="This is my comment",
                                   owner=user1, question=q)
        c.content = "This is my updated comment"
        c.save()

        c2 = Comment.objects.create(
            content="quick content", owner=user1, question=q)
        c2.delete()

        self.assertTrue(len(Comment.objects.all()) == 1)
        self.assertEqual(Comment.objects.get(owner=user1).question, q)

    def test_question_answer_instantiation(self):
        user1, _, a = obtain_sample_objects_as_tuple()
        c = Comment.objects.create(
            content="This is my comment to your answer", owner=user1, answer=a)
        c.content = "This is my updated comment"
        c.save()

        self.assertEqual(Comment.objects.get(owner=user1).answer, a)

        c2 = Comment.objects.create(
            content="quick content", owner=user1, answer=a)
        c2.delete()
        self.assertQuerysetEqual(
            Comment.objects.filter(content="quick content"), [])

    def test_comments_originator(self):
        user1, q, a = obtain_sample_objects_as_tuple()
        c1 = Comment.objects.create(
            content="quick content", owner=user1, answer=a)
        c2 = Comment.objects.create(
            content="quick content", owner=user1, question=q)

        self.assertIsNone(c1.question)
        self.assertIsNone(c2.answer)
        self.assertTrue(Comment.objects.count(), 2)


class VoteModel(TestCase):
    """Test cases for Vote model"""

    def setUp(self):
        user1 = User.objects.create_user(**credentials)
        title = "What is life?"
        content = "Someone please explain to me the purpose of life"
        Question.objects.create(title=title, content=content, owner=user1)

    def test_voting_score(self):
        create_many_users()
        _, q, _ = obtain_sample_objects_as_tuple()

        for user in User.objects.all():
            positive = random.choice([True, False])
            if positive:
                q.upvotes += 1
            else:
                q.downvotes += 1

            v = Vote.objects.create(question=q, user=user, positive=positive)
            self.assertIsNone(v.answer)
            self.assertIsNone(v.comment)

        self.assertTrue(q.score >= -15)
        self.assertTrue(q.score <= 15)
