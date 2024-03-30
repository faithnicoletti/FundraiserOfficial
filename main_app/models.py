from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.decorators import login_required


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount_donated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
   
    def __str__(self):
        return self.user.username


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class CommentSection(models.Model):
    participants = models.ManyToManyField(User, related_name='comment_sections')
    comments = models.ManyToManyField(Comment, related_name='comment_sections')
    timestamp = models.DateTimeField(auto_now_add=True)

class Fundraiser(models.Model):
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1200.00)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

    def __str__(self):
        return self.description

class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_donated = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username} donated {self.amount}!!! {self.timestamp}"

@login_required
class ProfilePayment(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)

@login_required
@receiver(post_save, sender=Profile)
def create_profile_payment(sender, instance, created, **kwargs):
    if created:
        ProfilePayment.objects.create(profile=instance)
