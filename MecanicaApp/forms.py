from django import forms


class registerForm(forms.Form):
    user = forms.CharField(label="Usuario", max_length=200, widget=forms.TextInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su corrreo'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese una contraseña'}))
    name = forms.CharField(label="Nombre", max_length=200, widget=forms.TextInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su nombre'}))
    last_name = forms.CharField(label="Apellido", max_length=200, widget=forms.TextInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su apellido'}))
    cellphone = forms.CharField(label="Telefono", max_length=200, widget=forms.NumberInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su Telefono'}))
    ci = forms.CharField(label="Cedula", max_length=200, widget=forms.NumberInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su cedula'}))
    direction = forms.CharField(label="Direccion", max_length=200, widget=forms.TextInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su direccion'}))
    email = forms.EmailField(label="Correo", widget=forms.EmailInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su corrreo'}))


# class customer_form(forms.Form):
class EmailForm(forms.Form):
    email = forms.EmailField(label="Ingresa tu correo", widget=forms.EmailInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su corrreo'}))


class passwordForm(forms.Form):
    password = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese una contraseña'}))
    password_confirmation = forms.CharField(label="Confirmar nueva contraseña", widget=forms.PasswordInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese una contraseña'}))


class tokenForm(forms.Form):
    token = forms.CharField(label="Ingrese el token enviado a su correo", max_length=10, widget=forms.TextInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese el token'}))


class loginForm(forms.Form):
    user = forms.CharField(label="Usuario", max_length=200, widget=forms.TextInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su corrreo'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese una contraseña'}))
