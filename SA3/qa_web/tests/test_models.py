"""
Submodule that defines test cases to be ran for models (object instantiation)
"""

import random
from django.test import TestCase
from qa_web.models import Question, Comment, Answer, User, Vote

credentials = {'username': 'johnny', 'password': 'password123'}


def obtain_sample_objects_as_tuple():
    """
    Helper method that obtains the first objects of each type
    of user and posts in the test database
    :return: Tuple of first user, first question, first answer
    """
    user1 = User.objects.first()
    question = Question.objects.first()
    answer = Answer.objects.first()
    return user1, question, answer


def create_many_users():
    """
    Helper method that creates many users in the test DB
    :return:
    """
    for i in range(0, 15):
        name = 'User{}'.format(i)
        password = str(i)
        _ = User.objects.create(username=name, password=password)
    return


class CommentModel(TestCase):
    """Test cases for Comment model"""

    def setUp(self):
        """
        Method that sets up the test case environment for
        testing of object instantiations
        """
        user1 = User.objects.create_user(**credentials)
        title = "What is life?"
        content = "Someone please explain to me the purpose of life"
        Question.objects.create(title=title, content=content, owner=user1)
        Answer.objects.create(
            content='Test answer', owner=user1, correct_answer=True)

    def test_to_string_method_question(self):
        """
        Tests the to string method for a question
        Was for coverage
        """
        _, question, _ = obtain_sample_objects_as_tuple()
        self.assertEqual(str(question), question.title)

    def test_get_answer_queryset(self):
        """
        Tests the get_answer_queryset function in
        Question model class
        """
        _, question, _ = obtain_sample_objects_as_tuple()
        self.assertEqual(None, question.get_answer_queryset().first())

    def test_question_comment_instantiation(self):
        """
        Tests the state and instantiation of a commment
        to a question
        """
        user1, question, _ = obtain_sample_objects_as_tuple()

        comment = Comment.objects.create(content="This is my comment",
                                         owner=user1, question=question)
        comment.content = "This is my updated comment"
        comment.save()

        second_comment = Comment.objects.create(
            content="quick content", owner=user1, question=question)
        second_comment.delete()

        self.assertTrue(len(Comment.objects.all()) == 1)
        self.assertEqual(Comment.objects.get(owner=user1).question, question)

    def test_question_answer_instantiation(self):
        """
        Tests the state and instantiation of a comment to
        an answer
        """
        user1, _, answer = obtain_sample_objects_as_tuple()
        comment = Comment.objects.create(
            content="This is my comment to your answer", owner=user1,
            answer=answer)
        comment.content = "This is my updated comment"
        comment.save()

        self.assertEqual(Comment.objects.get(owner=user1).answer, answer)

        second_comment = Comment.objects.create(
            content="quick content", owner=user1, answer=answer)
        second_comment.delete()
        self.assertQuerysetEqual(
            Comment.objects.filter(content="quick content"), [])

    def test_comments_originator(self):
        """
        Tests the number of questions owned by a user after
        instantiation
        """
        user1, question, answer = obtain_sample_objects_as_tuple()
        first_comment = Comment.objects.create(
            content="quick content", owner=user1, answer=answer)
        second_comment = Comment.objects.create(
            content="quick content", owner=user1, question=question)

        self.assertIsNone(first_comment.question)
        self.assertIsNone(second_comment.answer)
        self.assertTrue(Comment.objects.count(), 2)


class VoteModel(TestCase):
    """Test cases for Vote model"""

    def setUp(self):
        """
        Method that sets up the test case environment for
        testing of voting states
        """
        user1 = User.objects.create_user(**credentials)
        title = "What is life?"
        content = "Someone please explain to me the purpose of life"
        Question.objects.create(title=title, content=content, owner=user1)

    def test_voting_score(self):
        """
        Tests the functionality of a question's vote attribute
        """
        create_many_users()
        _, question, _ = obtain_sample_objects_as_tuple()

        for user in User.objects.all():
            positive = random.choice([True, False])
            if positive:
                question.upvotes += 1
            else:
                question.downvotes += 1

            vote = Vote.objects.create(question=question, user=user,
                                       positive=positive)
            self.assertIsNone(vote.answer)
            self.assertIsNone(vote.comment)

        self.assertTrue(question.score >= -15)
        self.assertTrue(question.score <= 15)
