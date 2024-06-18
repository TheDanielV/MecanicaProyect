import os

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from .forms import *
from services.AuthService.models import *
from .utils import *
from .models import *
from django.db import IntegrityError
from django.http import HttpResponse
from MecanicaApp.decorators import *
from django.shortcuts import render, redirect, get_object_or_404

AUTH_DATABASE = 'auth_db'
LOG_DATABASE = 'log_db'


def index(request):
    title = "MecanicaApp"
    client_ip = request.META.get('REMOTE_ADDR')
    print(client_ip)
    if request.session.get('token') is not None:
        return redirect('mostrarAutos')
    else:
        return render(request, 'index.html', {
            'title': title
        })


def register(request):
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            user = AuthUser()
            customer = Customer()
            try:
                token = user.create_user(form.cleaned_data.get('user'),
                                         form.cleaned_data.get('password'),
                                         form.cleaned_data.get('email'))
                customer.create(form.cleaned_data.get('name'), form.cleaned_data.get('last_name'),
                                form.cleaned_data.get('ci'), form.cleaned_data.get('cellphone'),
                                form.cleaned_data.get('direction'), token)
                user.save(using=AUTH_DATABASE)
                customer.save(using='default')
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
        if form.is_valid():
            auth_user = AuthUser()
            auth_key = auth_user.is_authorized(form.cleaned_data.get('user'),
                                               form.cleaned_data.get('password'))
            print("a")
            if auth_key is not None:
                request.session['token'] = auth_key
                return redirect("mostrarAutos")
            else:
                return render(request, 'AuthViews/login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = loginForm()
    return render(request, 'AuthViews/login.html', {'form': form})


@role_login_required(allowed_roles=['customer'])
def qr_code_view(request):
    person = None
    if request.session.get('role') == 'customer':
        person = Customer.get_customer(request.session.get('token'))

    img = generate_qr_code(encrypt_serializer_object(serialize_object(person)))
    return HttpResponse(img.getvalue(), content_type="image/png")


@role_login_required(allowed_roles=['customer'])
def qr_page(request):
    return render(request, 'MainApp/qrpagee.html',
                  {'user': request.session.get('full_name'), 'role': request.session.get('role')})


@role_login_required(allowed_roles=['customer'])
def mostrar_autos(request):
    try:
        customer = Customer.objects.get(token=request.session['token'])
        autos = Vehicle.objects.filter(customer=customer)
        return render(request, 'MainApp/contentAuto.html', {'autos': autos})
    except Customer.DoesNotExist:
        return render(request, 'AuthViews/register.html')


@role_login_required(allowed_roles=['customer'])
def registrar_auto(request):
    token = request.session.get('token')
    vehiculo = Vehicle()
    if request.method == 'POST':
        anio = request.POST.get('año')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        placa = request.POST.get('placa')
        color = request.POST.get('color')
        print(f'Entro en el controlador, datos: {anio} {placa}')
        try:
            customer = Customer.objects.get(token=request.session['token'])
            vehiculo.create_auto(customer, marca, modelo, placa, anio, color)
            vehiculo.save(using='default')
            return redirect("mostrarAutos")
        except Customer.DoesNotExist:
            return render(request, 'AuthViews/register.html')
    else:
        render(request, 'MainApp/registerAuto.html', {'error': 'Error al crear el vehículo'})
    return render(request, 'MainApp/registerAuto.html')


@role_login_required(allowed_roles=['employee'])
def mostrar_estacion(request):
    # Datos de ejemplo, estos datos deben provenir de tu base de datos
    vehiculos = [
        {
            'placa': 'PDB-1856',
            'especificaciones': 'Aceite sintético, 5W-30, 5 litros'
        },
        {
            'placa': 'XYZ-1234',
            'especificaciones': 'Aceite mineral, 10W-40, 4 litros'
        }
    ]
    return render(request, 'MainApp/contentEstacion.html', {'vehiculos': vehiculos})


def send_email_form(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)

        email = request.POST.get('email')
        try:
            passwordReset = PasswordReset()
            token = passwordReset.get_remember_password_token(email)
            # send_token_email(email, token)
            return redirect('enviarCorreo')
        except Exception as e:
            return render(request, 'AuthViews/emailInput.html', {'form': form, 'error': e})
    else:
        form = EmailForm()
        return render(request, 'AuthViews/emailInput.html', {'form': form})


def token_sended_test(request):
    if request.method == 'POST':
        form = tokenForm(request.POST)

        token = request.POST.get('token')
        try:
            passwordReset = PasswordReset()
            token_user = passwordReset.update_password_with_token(token)
            request.session['password_confirmation'] = token_user
            return redirect('confirmarContrasenia')
        except Exception as e:
            return render(request, 'AuthViews/tokenInput.html', {'form': form, 'error': e})
    else:
        form = tokenForm()
        return render(request, 'AuthViews/tokenInput.html', {'form': form})


def password_confirmation(request):
    if request.method == 'POST':
        form = passwordForm(request.POST)
        token_user = request.session.get('password_confirmation')
        password = request.POST.get('password')
        password_cofirm = request.POST.get('password_confirmation')
        if password_cofirm == password:
            try:
                auth_user = AuthUser()
                auth_user.update_password(token=token_user, password=password)
                logout_user(request)
                return redirect('login')
            except Exception as e:
                return render(request, 'AuthViews/tokenInput.html', {'form': form, 'error': e})
        else:
            return render(request, 'AuthViews/tokenInput.html', {'form': form})
    else:
        form = passwordForm()
        return render(request, 'AuthViews/tokenInput.html', {'form': form})


@role_login_required(allowed_roles=['customer'])
def eliminar_auto(request, auto_id):
    try:
        customer = Customer.objects.get(token=request.session['token'])
        vehiculo = get_object_or_404(Vehicle, id=auto_id, customer=customer)
        vehiculo.delete()
        messages.success(request, 'El vehículo ha sido eliminado exitosamente.')
    except Customer.DoesNotExist:
        messages.error(request, 'Cliente no encontrado.')
    except Vehicle.DoesNotExist:
        messages.error(request, 'Vehículo no encontrado.')

    return redirect('mostrarAutos')


def logout_user(request):
    logout(request)
    return redirect('index')

def ordenar_servicio(request):
    return render(request, 'MainApp/orderServicio.html')