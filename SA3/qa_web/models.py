from django.db import models


class Post(models.Model):
    content = models.TextField()
    owner = models.CharField(max_length=30)
    creation_date = models.DateTimeField(auto_now_add=True)

