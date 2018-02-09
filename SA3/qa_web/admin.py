from django.contrib import admin
from .models import Post
from .models import Questions
from .models import Answers

admin.site.register(Post)
admin.site.register(Questions)
admin.site.register(Answers)
