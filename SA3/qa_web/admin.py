"""Admin Website Settings
Used to register models for interaction through the admin website.
Superuser credentials are found in the README or create through manage.py.

For more information: https://docs.djangoproject.com/en/2.0/ref/contrib/admin/
"""
from django.contrib import admin
from .models import Questions, Answers, Comments, User
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)
admin.site.register(Questions)
admin.site.register(Answers)
admin.site.register(Comments)
