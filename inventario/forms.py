from django import forms
from .models import Articulo, User
from django.contrib.auth.forms import AuthenticationForm

class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ["nombre", "descripcion", "cantidad", "asignacion", "valor", "foto"]

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={"class": "form-control"}))