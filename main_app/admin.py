from django.contrib import admin
from django.db.models import Sum
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
        # Calculate the total amount donated by summing up all donation amounts related to the profile
        total_donated = ProfilePayment.objects.filter(profile=obj).aggregate(total_donated=Sum('donation_amount'))['total_donated'] or 0
        return total_donated

    total_amount_donated.short_description = 'Total Amount Donated'  # Set the column header for total_amount_donated

class ProfilePaymentAdmin(admin.ModelAdmin):
    list_display = ['donation_amount', 'profile', 'timestamp', 'current_amount']

    def current_amount(self, obj):
        # Get the total current amount of donations
        return ProfilePayment.objects.aggregate(current_amount=Sum('donation_amount'))['current_amount'] or 0

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfilePayment, ProfilePaymentAdmin)


