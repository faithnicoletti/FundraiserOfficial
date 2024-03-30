import stripe 
import psycopg2
import time
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash, authenticate, logout
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm
)
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse
from .models import Profile, ProfilePayment
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .models import CommentSection, Comment, Profile, Fundraiser, Donation, ProfilePayment, create_profile_payment
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import RequestContext, context
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    return render(request, 'home.html')


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

    context = {'user': user, 'profile': profile}
    return render(request, 'profile.html', context)


def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)

    args = {'form': form}
    return render(request, 'edit_profile.html', args)

class EditProfileForm(LoginRequiredMixin, UserChangeForm):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name'

        )


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('profile')
        else:
            return redirect('change-password')

    else:
        form = PasswordChangeForm(user=request.user)

        args = {'form': form}
        return render(request, 'change_password.html', args)


class DeleteUser(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'delete_user_confirm.html'
    success_message = "User has been deleted"
    success_url = reverse_lazy('home')

@login_required
def charge(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        checkout_session = stripe.checkout.Session.create(
            payment_method_types = ['card'],
            line_items=[
        {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Donation',
                },
                'unit_amount': 1000,  # Amount in cents
            },
            'quantity': 1,
        },
    ],
            mode = 'payment',
            customer_creation = 'always',
            success_url = settings.REDIRECT_DOMAIN + '/payment_successful?session_id={CHECKOUT_SESSION_ID}',
            cancel_url = settings.REDIRECT_DOMAIN + '/payment_cancelled'
        )
        return redirect(checkout_session.url, code=303)
    return render(request, 'charge.html')


## use Stripe dummy card: 4242 4242 4242 4242
def payment_successful(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session_id = request.GET.get('session_id', None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    customer = stripe.Customer.retrieve(session.customer)
    
    # Retrieve the profile associated with the current user
    profile = request.user.profile
    
    try:
        # Retrieve the associated UserPayment object using the profile
        user_payment = profile.profilepayment
        user_payment.stripe_checkout_id = checkout_session_id
        user_payment.save()
    except ProfilePayment.DoesNotExist:
        # Handle the case where UserPayment object doesn't exist
        pass
    
    return render(request, 'payment_successful.html', {'customer': customer})


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
		user_payment = UserPayment.objects.get(stripe_checkout_id=session_id)
		user_payment.payment_bool = True
		user_payment.save()
	return HttpResponse(status=200)

# @require_POST
# @login_required
# def create_payment_intent(request):
#     amount_usd = 10.99  # Set the amount in USD
#     try:
#         intent = stripe.PaymentIntent.create(
#             amount=int(amount_usd * 100),  # Stripe expects amount in cents
#             currency="usd",  # Currency in USD
#             automatic_payment_methods={"enabled": True},
#         )
#         return JsonResponse({'client_secret': intent.client_secret})
#     except stripe.error.StripeError as e:
#         # Handle Stripe errors
#         return JsonResponse({'error': str(e)}, status=500)

# @login_required
# def charge(request):
#     if request.method == 'POST':
#         amount = request.POST.get('amount', 0)
#         print('Data:', request.POST)
#         return redirect(reverse('success', args=[amount]))
#     else:
#         return render(request, 'charge.html')

# @login_required
# def successMsg(request, args):
#     amount = args 

#     return render(request, 'success.html', {'amount': amount})

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

