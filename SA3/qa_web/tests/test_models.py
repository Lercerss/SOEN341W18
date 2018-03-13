from django.test import TestCase
from django.contrib.auth import authenticate
from qa_web.models import Questions, Comments, Answers, User, Vote

import random

credentials = {'username' : 'johnny', 'password' :'password123'}

def obtain_sample_objects_as_tuple():

    user1 = User.objects.first()
    q = Questions.objects.first()
    a = Answers.objects.first()
    return user1, q, a

def create_many_users():

    for i in range(0,15):
        name = 'User{}'.format(i)
        pw = '{}'.format(i)
        u = User.objects.create(username = name, password= pw)
    return

class CommentModel(TestCase):

    def setUp(self):
        User.objects.create_user(**credentials)
        user1 = User.objects.first()
        title = "What is life?"
        content = "Someone please explain to me the purpose of life"
        q = Questions.objects.create(title=title, content=content, owner=user1)
        a = Answers.objects.create(content= 'Test answer', owner = user1, correct_answer= True)

    def test_question_comment_instantiation(self):

        # testing comments for question only
        user1, q, _ = obtain_sample_objects_as_tuple()

        comment1 = "This is my comment"
        c = Comments.objects.create(content=comment1, owner=user1, question=q)
        comment2 = "This is my updated comment"
        c.content = comment2
        c.save()

        c2 = Comments.objects.create(content="quick content", owner=user1, question=q)
        c2.delete()

        self.assertTrue(len(Comments.objects.all()) == 1)
        self.assertEqual(Comments.objects.get(owner=user1).question, q)


    def test_question_answer_instantiation(self):

        # testing comments for answers only
        user1, _, a = obtain_sample_objects_as_tuple()

        # testing comments for question only
        comment1 = "This is my comment to your answer"
        c = Comments.objects.create(content=comment1, owner=user1, answer=a)
        comment2 = "This is my updated comment"
        c.content = comment2
        c.save()

        self.assertEqual(Comments.objects.get(owner=user1).answer, a)

        c2 = Comments.objects.create(content="quick content", owner=user1, answer=a)
        c2.delete()

    def test_comments_originator(self):

        user1, q, a = obtain_sample_objects_as_tuple()
        c1 = Comments.objects.create(content="quick content", owner=user1, answer=a)
        c2 = Comments.objects.create(content="quick content", owner=user1, question=q)

        self.assertIsNone(c1.question)
        self.assertIsNone(c2.answer)
        self.assertTrue(Comments.objects.count(), 2)


class VoteModel(TestCase):

    def setUp(self):
        user1 = User.objects.first()
        title = "What is life?"
        content = "Someone please explain to me the purpose of life"
        q = Questions.objects.create(title=title, content=content, owner=user1)

    def test_voting_score(self):
        create_many_users()
        _, q, _ = obtain_sample_objects_as_tuple()

        for user in User.objects.all():

            positive = random.choice([True, False])
            if positive:
                q.upvotes += 1
            else:
                q.downvotes += 1

            v = Vote.objects.create(question = q, user=user, positive=positive)
            self.assertIsNone(v.answer)
            self.assertIsNone(v.comment)

        self.assertTrue(q.score >= -15)
        self.assertTrue(q.score <= 15)
