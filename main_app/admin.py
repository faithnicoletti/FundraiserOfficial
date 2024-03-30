from django.contrib import admin
from django.contrib.auth.models import User
from .models import CommentSection, Profile, Comment, Fundraiser, ProfilePayment
# Register your models here.



admin.site.register(CommentSection)

admin.site.register(Comment)

admin.site.register(Fundraiser)


class ProfilePaymentInline(admin.TabularInline):
    model = ProfilePayment
    extra = 0  # Show all existing ProfilePayment instances

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProfilePaymentInline]

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_amount_donated']
admin.site.register(ProfilePayment)