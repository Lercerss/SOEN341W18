from django.contrib import admin
from .models import Questions, Answers, Comments, Tags

admin.site.register(Questions)
admin.site.register(Answers)
admin.site.register(Comments)
admin.site.register(Tags)
