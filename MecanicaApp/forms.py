from django import forms


class registerForm(forms.Form):
    user = forms.CharField(label="Usuario", max_length=200, widget=forms.TextInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su corrreo'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese una contraseña'}))
    email = forms.EmailField(label="Correo", widget=forms.EmailInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su corrreo'}))


class loginForm(forms.Form):
    user = forms.CharField(label="Usuario", max_length=200, widget=forms.TextInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su corrreo'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese una contraseña'}))
