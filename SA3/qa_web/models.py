from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    """
    Parent meta class that describes a post as a publication on the website with certain content
    created by a certain owner
    This will be used for inheritance
    """
    content = models.TextField(null=True)
    owner = models.ForeignKey(User, null= True, on_delete=models.SET_NULL)
    creation_date = models.DateTimeField(auto_now_add=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    class Meta:
        abstract = True

class Questions(Post):
    """
    The question (or thread) initiates the interaction between users' answers,
    comments, and voting
    """
    title = models.CharField(max_length=300, null=True)
    visits = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    
class Answers(Post):
    """
    The answer is a proposed solution to a certain question
    There can be many answers to a question and there is only one correct answer per question
    """
    question = models.ForeignKey(Questions, null=True, on_delete=models.CASCADE)
    correct_answer = models.BooleanField(default = False)

class Comments(Post):
    """
    A comment can be posted for an entire question or an answer
    There can be many comments to questions and answers
    """
    question = models.ForeignKey(Questions, null=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answers, null=True, on_delete=models.CASCADE)
    
class Tags(models.Model):
    """
    One or multiple tags can be assigned to a question, in order to classify the question
    There can be many tags to a question
    """
    question = models.ForeignKey(Questions, null= True, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, null=True)
    