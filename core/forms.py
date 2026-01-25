from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # import your CustomUser
import core.message_language as ml

class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label=ml.get_message('email'),
        widget=forms.EmailInput(attrs={
            'placeholder': ml.get_message('email'),
            'class': 'input-field',
        })
    )

    password = forms.CharField(
        required=True,
        label=ml.get_message('password'),
        widget=forms.PasswordInput(attrs={
            'placeholder': ml.get_message('password'),
            'class': 'input-field',
        })
    )
    
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label=ml.get_message('add_email'),
        widget=forms.EmailInput(attrs={
            'placeholder': ml.get_message('email'),
            'class': 'input-field',
        })
    )

    username = forms.CharField(
        label=ml.get_message('add_username'),
        widget=forms.TextInput(attrs={
            'placeholder': ml.get_message('username'),
            'class': 'input-field',
        })
    )

    password1 = forms.CharField(
        label=ml.get_message('add_password'),
        widget=forms.PasswordInput(attrs={
            'placeholder': ml.get_message('password'),
            'class': 'input-field',
        })
    )

    password2 = forms.CharField(
        label= ml.get_message('confirm_password'),
        widget=forms.PasswordInput(attrs={
            'placeholder': ml.get_message('password'),
            'class': 'input-field',
        })
    )

    class Meta:
        model = CustomUser  # ATTENTION: now point to your model
        fields = ('username', 'email', 'password1', 'password2')
