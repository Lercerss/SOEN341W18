from django.test import TestCase
from django.contrib.auth import authenticate
from qa_web.models import Questions, Comments, User


class ModelTest(TestCase):

    def test_comments(self):
        uname = 'johnny'
        pw = 'password123'
        user1 = authenticate(username=uname, password=pw)

        title = "What is life?"
        content = "Someone please explain to me the purpose of life"
        q = Questions.objects.create(title=title, content=content, owner=user1)

        # testing comments for question only
        comment1 = "This is my comment"
        c = Comments.objects.create(content=comment1, owner=user1, question=q)
        comment2 = "This is my updated comment"
        c.content = comment2
        c.save()

        self.assertTrue(len(Comments.objects.all()) == 1)
        self.assertEqual(Comments.objects.get(owner=user1).question, q)
