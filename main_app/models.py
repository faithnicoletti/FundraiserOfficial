from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Sum


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class ProfilePayment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    payment_bool = models.BooleanField(default=False)
    donation_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(default=datetime)
    stripe_checkout_id = models.CharField(max_length=500)

    def update_total_amount_donated(self):
        # Calculate the sum of all donations related to this profile
        total_donated = ProfilePayment.objects.filter(profile=self.profile).aggregate(total_donated=Sum('donation_amount'))['total_donated'] or 0
        # Update the total_amount_donated field in the related profile
        self.profile.total_amount_donated = total_donated
        self.profile.save()

    def __str__(self):
        return f"Donation Amount: {self.donation_amount}, Profile: {self.profile}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_total_amount_donated()

    @property
    def current_amount(self):
        # Get the total current amount of donations
        return ProfilePayment.objects.aggregate(current_amount=Sum('donation_amount'))['current_amount'] or 0

    @property
    def goal_amount(self):
        # Set your desired goal amount
        return 2000.00


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(default='your comment')
    timestamp = models.DateTimeField(auto_now_add=True)

class CommentSection(models.Model):
    participants = models.ManyToManyField(User, related_name='comment_sections')
    comments = models.ManyToManyField(Comment, related_name='comment_sections')
    timestamp = models.DateTimeField(auto_now_add=True)

