from django import forms
from .models import Articulo, User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ["nombre", "descripcion", "cantidad", "asignacion", "valor", "foto", "categoria"]

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    email_confirm = forms.EmailField(required=True, label="Confirmar correo electrónico")

    class Meta:
        model = User
        fields = ["username", "email", "email_confirm", "password1", "password2"]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_confirm = cleaned_data.get("email_confirm")
        username = cleaned_data.get("username")

        # Verificar si el email ya está registrado
        if email and User.objects.filter(email=email).exists():
            self.add_error("email", "Este correo electrónico ya está registrado.")

        # Verificar si el username ya está registrado
        if username and User.objects.filter(username=username).exists():
            self.add_error("username", "Este nombre de usuario ya está en uso.")

        # Verificar que los correos electrónicos coincidan
        if email and email_confirm and email != email_confirm:
            self.add_error("email_confirm", "Los correos electrónicos no coinciden.")

        return cleaned_data


class LoginForm(forms.Form):  # No extendemos AuthenticationForm
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )




    