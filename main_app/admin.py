from django.contrib import admin
from django.contrib.auth.models import User
from .models import CommentSection, Profile, Comment
# Register your models here.

admin.site.register(Profile)

admin.site.register(CommentSection)
# Register your models here.
admin.site.register(Comment)
