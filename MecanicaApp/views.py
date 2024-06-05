from django.shortcuts import render, redirect
from .forms import registerForm, loginForm
from services.models import AuthUser
from django.http import HttpResponse


def index(request):
    title = "MecanicaApp"
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
            user.save(using='auth_db')
            print("Usuario: " + str(user.username) + ", PasswordHashed: " + str(user.password))
            return render(request, 'index.html')
    else:
        # Si es una solicitud GET, mostrar el formulario vacío
        form = registerForm()
    return render(request, 'AuthViews/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = loginForm(request.POST)
