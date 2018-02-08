from django.db import models


class Post(models.Model):
    content = models.TextField()
    owner = models.CharField(max_length=30)
    creation_date = models.DateTimeField(auto_now_add=True)

class Questions(Post):
    title = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.title

