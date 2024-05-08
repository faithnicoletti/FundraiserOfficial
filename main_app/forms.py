from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm,UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

# class CustomUserChangeForm(UserChangeForm):
#     email = forms.EmailField(required=True)
#     first_name = forms.CharField(max_length=250)
#     last_name = forms.CharField(max_length=250)
#     username = forms.Charfield(max_length=250)

#     class Meta:
#         model = User
#         fields = ('username', 'first_name', 'last_name', 'email')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields.pop('password')
        
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs['class'] = 'form-control text-white'

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password')

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control text-white'

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control text-white'

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control text-white'

class CustomSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=250)
    last_name = forms.CharField(max_length=250)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control text-white'