import stripe 
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash, authenticate
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm
)
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import Profile
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .models import CommentSection
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import RequestContext, context

def home(request):
    return render(request, 'home.html')


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=250)
    last_name = forms.CharField(max_length=250)


class Meta(UserCreationForm.Meta):
    model = User
    fields = ('username', 'name','email','password1', 'password2')


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.name = form.cleaned_data['name']
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

        form = EditProfileForm(
            request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            name = form.cleaned_data['name']
            if name:
                request.user.profile.name = name
                request.user.profile.save()
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
            'name',

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
def comment_section(request, other_username):
    user = request.user
    other_username = User.objects.get(username=other_username)
    
    if request.method == 'POST':
        message = request.POST['message']
        comment_section = CommentSection.objects.create(user=user, other_user=other_username, message=message)
       
    comment_sections = CommentSection.objects.all().order_by('-timestamp')
    
    context = {'user': user, 'other_user': other_username, 'comment_sections': comment_sections}
    return render(request, 'comment_section.html', context)


def comment_history(request):
    all_comments = CommentSection.objects.all().order_by('-timestamp')

    context = {'all_comments': all_comments}
    return render(request, 'comment_history.html', context)
