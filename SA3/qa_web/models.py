"""Models define how data is to be stored in the database using ORM.
For more information on how this works: https://docs.djangoproject.com/en/2.0/topics/db/models/
For more information on how the project's data is organised:
    https://github.com/Lercerss/SOEN341W18/wiki/Architecture-Block-Diagram
"""
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager


class User(AbstractUser):
    """Model for Users of the website, including personal information as well as data required for authentication"""
    age = models.IntegerField(null=True)
    birthday = models.DateField(null=True)
    motherland = models.TextField(max_length=100, null=True)
    school = models.TextField(max_length=100, null=True)
    major = models.CharField(max_length=50, null=True)
    city = models.TextField(max_length=100, null=True)


class Post(models.Model):
    """Parent meta class that describes a post as a publication on the website"""
    content = models.TextField(null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    creation_date = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    class Meta:
        abstract = True

    @property
    def score(self):
        """Returns an integer value based on the number of votes on the Post."""
        return self.upvotes - self.downvotes


class Question(Post):
    """A Question is the first element of a thread in the website which serves to start a discussion.
    All other data elements relate to one or multiple Questions.
    """
    title = models.CharField(max_length=300, null=True)
    visits = models.IntegerField(default=0)
    voters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='q_voters', through='Vote')
    tag = TaggableManager(blank=True)

    def __str__(self):
        return self.title

    def get_answer_queryset(self):
        return Answer.objects.filter(question=self)


class Answer(Post):
    """An Answer is a response to a Question, the first level of reply in the discussion.
    An Answer cannot exist without a Question.
    """
    question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE)
    correct_answer = models.BooleanField(default=False)
    voters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='a_voters', through='Vote')


class Comment(Post):
    """A Comment is a lower-level response to either an Answer or Question.
    It is the second level of discussion as it might not directly relate to the Question's matter.
    """
    question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, on_delete=models.CASCADE)
    voters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='c_voters', through='Vote')


class Vote(models.Model):
    """Defines the relationship between a user voting and the post.
    A vote can be positive or negative (not positive), allowing the full range of integer scores.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    positive = models.BooleanField()
