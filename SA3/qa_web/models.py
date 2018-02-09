from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    content = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)

class Questions(Post):
    title = models.CharField(max_length=300)
    def __str__(self):
        return self.title

