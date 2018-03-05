from django.contrib import admin
from .models import Questions, Answers, Comments, User
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)
admin.site.register(Questions)
admin.site.register(Answers)
admin.site.register(Comments)
