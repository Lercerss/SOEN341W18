from django.db import models
from django.contrib import admin


class User(models.Model):
    username = models.CharField(max_length=70)
    password = models.CharField(max_length=70)

admin.site.register(User)