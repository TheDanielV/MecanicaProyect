import os

from django.shortcuts import render, redirect
from .forms import registerForm, loginForm
from services.AuthService.models import *
from .utils import *
from django.db import IntegrityError
from django.http import HttpResponse


AUTH_DATABASE = 'auth_db'
LOG_DATABASE = 'log_db'


def index(request):
    title = "MecanicaApp"
    client_ip = request.META.get('REMOTE_ADDR')
    print(client_ip)
    return render(request, 'index.html', {
        'title': title
    })


def register(request):
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            user = AuthUser()

            try:
                user.create_user(form.cleaned_data.get('user'),
                                 form.cleaned_data.get('password'),
                                 form.cleaned_data.get('email'))

                user.save(using=AUTH_DATABASE)

                return render(request, 'index.html', {
                    'title': "Usuario Creado"
                })
            except IntegrityError as e:
                # voy a reenviar el mismo formulario con los datos mismos datos, excepto contraseña
                return render(request, 'AuthViews/register.html', {'form': form, 'error': e})
            except InvalidPassword as e:
                return render(request, 'AuthViews/register.html', {'form': form, 'error': e})
    else:
        # Si es una solicitud GET, mostrar el formulario vacío
        form = registerForm()
    return render(request, 'AuthViews/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = loginForm(request.POST)


def qr_code_view(request):
    secret_key = os.urandom(32)
    print(secret_key)  # Guarda esta clave de manera segura
    img = None
    return HttpResponse(img.getvalue(), content_type="image/png")
