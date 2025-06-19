from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # Importa tu CustomUser

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo electrónico',
            'class': 'input-field',
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre de usuario',
            'class': 'input-field',
        })
    )

    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'input-field',
        })
    )

    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmar contraseña',
            'class': 'input-field',
        })
    )

    class Meta:
        model = CustomUser  # ATENCIÓN: ahora apunta a tu modelo
        fields = ('username', 'email', 'password1', 'password2')
