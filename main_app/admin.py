from django.contrib import admin
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import CommentSection, Profile, Comment, ProfilePayment

admin.site.register(CommentSection)
admin.site.register(Comment)

class ProfilePaymentInline(admin.TabularInline):
    model = ProfilePayment
    extra = 0 

class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProfilePaymentInline]
    readonly_fields = ['total_amount_donated']

    list_display = ['user', 'total_amount_donated']

    def total_amount_donated(self, obj):
        total_donated = ProfilePayment.objects.filter(profile=obj).aggregate(total_donated=Sum('donation_amount'))['total_donated'] or 0
        return total_donated
    total_amount_donated.short_description = 'Total Amount Donated'

class ProfilePaymentAdmin(admin.ModelAdmin):
    list_display = ['donation_amount', 'profile', 'timestamp', 'current_amount']

    def current_amount(self, obj):
       
        return ProfilePayment.objects.aggregate(current_amount=Sum('donation_amount'))['current_amount'] or 0

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfilePayment, ProfilePaymentAdmin)


