import stripe 
import psycopg2
import time
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserChangeForm, CustomPasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.http import JsonResponse
from .models import Profile, ProfilePayment
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .models import CommentSection, Comment, Profile, ProfilePayment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import RequestContext, context
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
   current_amount = ProfilePayment.objects.aggregate(current_amount=Sum('donation_amount'))['current_amount'] or 0
   goal_amount = ProfilePayment().goal_amount

   current_amount_float = float(current_amount)

   percentage = (current_amount_float / goal_amount) * 100

   recent_donations = ProfilePayment.objects.order_by('-timestamp')[:5]

   context = {'current_amount': current_amount, 'percentage': percentage, 'recent_donations': recent_donations}
   return render(request, 'home.html', context)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=250)
    last_name = forms.CharField(max_length=250)


class Meta(UserCreationForm.Meta):
    model = User
    fields = ('username', 'first_name','last_name', 'email','password1', 'password2')


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            profile = Profile.objects.create(
                user=user,
            )
            login(request, user)
            return redirect('profile')
        else:
            error_message = 'Invalid sign up - try again'
    else:
        form = SignUpForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)


@login_required
def profile(request):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)

    total_amount_donated = ProfilePayment.objects.filter(profile=profile).aggregate(total_amount_donated=Sum('donation_amount'))['total_amount_donated'] or 0

    context = {'user': user, 'profile': profile, 'total_amount_donated': total_amount_donated}
    return render(request, 'profile.html', context)


def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile successfully updated.')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})


def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password successfully changed.')
            return redirect('profile')
        else:
            return redirect('change-password')

    else:
        form = CustomPasswordChangeForm(user=request.user)

    args = {'form': form}
    return render(request, 'change_password.html', args)


class DeleteUser(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'delete_user_confirm.html'
    success_message = "User has been deleted"
    success_url = reverse_lazy('home')

from django.http import HttpResponseBadRequest
import re

@login_required
def charge(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    current_amount = ProfilePayment.objects.aggregate(current_amount=Sum('donation_amount'))['current_amount'] or 0
    goal_amount = ProfilePayment().goal_amount

    current_amount_float = float(current_amount)
    percentage = (current_amount_float / goal_amount) * 100

    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount_in_cents = int(float(amount) * 100)
        except ValueError:
            messages.error(request, 'Invalid input. Please enter a valid donation amount.')
            return render(request, 'charge.html', {'current_amount': current_amount, 'percentage': percentage})

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Donation',
                        },
                        'unit_amount': amount_in_cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            customer_creation='always',
            success_url=settings.REDIRECT_DOMAIN + '/payment_successful?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings.REDIRECT_DOMAIN + '/payment_cancelled'
        )
        return redirect(checkout_session.url, code=303)

    return render(request, 'charge.html', {'current_amount': current_amount, 'percentage': percentage})

## use Stripe dummy card: 4242 4242 4242 4242
@login_required
def payment_successful(request):
    if request.method == 'GET':
        checkout_session_id = request.GET.get('session_id')
        try:
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            customer = stripe.Customer.retrieve(session.customer)
            
            profile, created = Profile.objects.get_or_create(user=request.user)
            
            profile_payment = ProfilePayment.objects.create(
                profile=profile,
                stripe_checkout_id=checkout_session_id,
                payment_bool=True,
                donation_amount=session.amount_total / 100, 
                timestamp=datetime.now()
            )
            
            return render(request, 'payment_successful.html', {'customer': customer})
        except Exception as e:
        
            messages.error(request, "Payment failed. Please try again.")
            return redirect('home')


def payment_cancelled(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY
	return render(request, 'payment_cancelled.html/')


@csrf_exempt
def stripe_webhook(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY
	time.sleep(10)
	payload = request.body
	signature_header = request.META['HTTP_STRIPE_SIGNATURE']
	event = None
	try:
		event = stripe.Webhook.construct_event(
			payload, signature_header, settings.STRIPE_WEBHOOK_SECRET_TEST
		)
	except ValueError as e:
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		return HttpResponse(status=400)
	if event['type'] == 'checkout.session.completed':
		session = event['data']['object']
		session_id = session.get('id', None)
		time.sleep(15)
		user_payment = ProfilePayment.objects.get(stripe_checkout_id=session_id)
		user_payment.payment_bool = True
		user_payment.save()
	return HttpResponse(status=200)

@login_required
def comment_section(request, other_username):
    user = request.user
    other_user = User.objects.get(username=other_username)
    
    if request.method == 'POST':
        message = request.POST['message']
        print("Received message:", message)
        comment = Comment.objects.create(user=user, content=message)
        comment_section = CommentSection.objects.create()
        comment_section.participants.set([user, other_user])
        comment_section.comments.set([comment])
       
    all_comments = Comment.objects.all().order_by('-timestamp')
    
    context = {'user': user, 'other_user': other_username, 'all_comments': all_comments}
    return render(request, 'comment_section.html', context)


def comment_history(request):
    all_comments = CommentSection.objects.all().order_by('-timestamp')

    context = {'all_comments': all_comments}
    return render(request, 'comment_history.html', context)

