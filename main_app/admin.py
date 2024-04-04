from django.contrib import admin
from django.contrib.auth.models import User
from .models import CommentSection, Profile, Comment, ProfilePayment
# Register your models here.



admin.site.register(CommentSection)

admin.site.register(Comment)


class ProfilePaymentInline(admin.TabularInline):
    model = ProfilePayment
    extra = 0  # Show all existing ProfilePayment instances

class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProfilePaymentInline]
    readonly_fields = ['total_amount_donated']  # Make total_amount_donated field read-only

    list_display = ['user', 'total_amount_donated']  # Add 'total_amount_donated' to list display

    def total_amount_donated(self, obj):
        return obj.total_amount_donated  # Define a method to display total_amount_donated in admin list display

    total_amount_donated.short_description = 'Total Amount Donated'  # Set the column header for total_amount_donated

admin.site.register(Profile, ProfileAdmin)


