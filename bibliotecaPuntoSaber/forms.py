from django import forms
from .models import Archivo, Usuario
from django.contrib.auth.forms import UserCreationForm

class ArchivoForm(forms.ModelForm):
    class Meta:
        model = Archivo
        fields = ["titulo", "descripcion", "archivo", "autor", "categoria"]

class UsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ["username", "email", "first_name", "last_name", "rol", "estado"]