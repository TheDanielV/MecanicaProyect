from django.shortcuts import render, redirect
from .forms import registerForm, loginForm
from services.AuthService.models import *
from services.logs.models import *
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
            user.create_user(form.cleaned_data.get('user'), form.cleaned_data.get('password'),
                             form.cleaned_data.get('email'))
            try:
                user.save(using=AUTH_DATABASE)
                # Prueba del log de inicio correcto por que me da pereza hacer un login
                log = AuthLog()
                log.create_log(request.META.get('REMOTE_ADDR'),
                               AuthLog.EventType.LOGIN_SUCCESS.name)
                log.save(using=LOG_DATABASE)
                return render(request, 'index.html')

            except IntegrityError as e:
                log = AuthLog()
                print(request.META.get('REMOTE_ADDR'))
                log.create_log(request.META.get('REMOTE_ADDR'),
                               AuthLog.EventType.LOGIN_FAILURE.name)
                log.save(using=LOG_DATABASE)

                # voy a reenviar el mismo formulario con los datos mismos datos, excepto contraseña
                return render(request, 'AuthViews/register.html', {'form': form})
    else:
        # Si es una solicitud GET, mostrar el formulario vacío
        form = registerForm()
    return render(request, 'AuthViews/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = loginForm(request.POST)
