from django import forms
from django.core.exceptions import ValidationError


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


class loginForm(forms.Form):
    user = forms.CharField(label="Usuario", max_length=200, widget=forms.TextInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese su corrreo'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(
        attrs={'class': 'input form-control', 'placeholder': 'Ingrese una contraseña'}))


class crearServicioForm(forms.Form):
    nombreServicio = forms.CharField(
        label="Nombre",
        max_length=400,
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Ingrese el nombre del servicio'
        })
    )
    descripcionServicio = forms.CharField(
        label="Descripción",
        max_length=800,
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Ingrese la descripción del servicio'
        })
    )
    precioServicio = forms.DecimalField(
        label="Precio",
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Ingrese el precio del servicio'
        }),
        error_messages={
            'invalid': 'Por favor, ingrese un valor numérico válido.',
        }
    )

    def clean_precioServicio(self):
        precio = self.cleaned_data.get('precioServicio')
        if precio is not None and precio.as_integer_ratio()[1] > 100:  # Chequea los decimales
            raise ValidationError('El precio no puede tener más de 2 decimales.')
        return precio
