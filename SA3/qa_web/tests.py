from django.test import TestCase
from django.contrib.auth import authenticate
from .forms import UserProfile
from .models import Questions,Comments

# Create your tests here.
class form_validation(TestCase):

    def test_some_profile(self):
        form_data = {'prename': 'John', 'surname': 'Smith',
                     'email':'test@example.com', 'age':40, 'birthday': '1960-08-24',
                     'motherland':'le quebec', 'school': 'McGill University',
                     'major': 'COMP SCI', 'city':'Montreal'}
        form = UserProfile(data=form_data)
        self.assertTrue(form.is_valid())


class instance_creation(TestCase):

    def test_comments(self):
        uname = 'johnny'
        pw = 'password123'
        user1 = authenticate(username=uname, password=pw)

        title = "What is life?"
        content = "Someone please explain to me the purpose of life"
        q = Questions.objects.create(title=title, content=content, owner= user1)

        #testing comments for question only
        comment1 = "This is my comment"
        c = Comments.objects.create(content = comment1, owner= user1, question=q)
        comment2 = "This is my updated comment"
        c.content= comment2
        c.save()