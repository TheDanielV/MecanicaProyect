from django import forms


class registerForm(forms.Form):
    user = forms.CharField(label="Usuario", max_length=200)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    email = forms.EmailField(label="Correo")


class loginForm(forms.Form):
    user = forms.CharField(label="Usuario", max_length=200)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
