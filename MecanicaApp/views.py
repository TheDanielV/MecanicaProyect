import os

from django.shortcuts import render, redirect
from .forms import registerForm, loginForm, crearServicioForm
from services.AuthService.models import *
from .utils import *
from .models import *
from django.db import IntegrityError
from django.http import HttpResponse
from MecanicaApp.decorators import *
from django.shortcuts import render, get_object_or_404, redirect


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
            customer = Customer()
            try:
                token = user.create_user(form.cleaned_data.get('user'),
                                         form.cleaned_data.get('password'),
                                         form.cleaned_data.get('email'))
                customer.create(form.cleaned_data.get('name'), form.cleaned_data.get('last_name'), form.cleaned_data.get('ci'), form.cleaned_data.get('cellphone'),form.cleaned_data.get('direction'), token)
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
                return redirect("qr")
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

    # secret_key = os.urandom(32)
    img = generate_qr_code(serialize_object(person))
    return HttpResponse(img.getvalue(), content_type="image/png")


@role_login_required(allowed_roles=['customer'])
def qr_page(request):
    return render(request, 'MainApp/qrpagee.html', {'user': request.session.get('full_name')})


def mostrar_autos(request):
    return render(request, 'MainApp/contentAuto.html')


def registrar_auto(request):
    return render(request, 'MainApp/registerAuto.html')



def mostrar_servicios(request):
    services = [
        {"id": 1, "nombre": "Servicio 1", "descripcion": "Desdddddción 1", "precio": 100},
        {"id": 2, "nombre": "Servicio 2", "descripcion": "Descripción 2", "precio": 200},
        # Agrega más servicios según sea necesario
    ]
    context = {
        'services': services
    }
    return render(request, 'MainApp/contentServices.html',context)

def crearServicios(request):
    if request.method == 'POST':
        form = crearServicioForm(request.POST)
        if form.is_valid():
            # Aquí asumimos que tienes un modelo para el servicio y un método save en el formulario
            # Si no, deberías manejar el guardado del servicio aquí manualmente
            form.save()
            return redirect('mostrarServicios')
    else:
        form = crearServicioForm()
    return render(request, 'MainApp/crear_servicio.html', {'form': form})


def editarServicios(request, service_id):
    servicios_data = [
        {"id": 1, "nombre": "Servicio 1", "descripcion": "Descripción 1", "precio": 100},
        {"id": 2, "nombre": "Servicio 2", "descripcion": "Descripción 2", "precio": 200},
        # Agrega más servicios según sea necesario
    ]

    # Encuentra el servicio por su id
    servicio = next((s for s in servicios_data if s["id"] == service_id), None)
    if not servicio:
        return render(request, '404.html', status=404)

    if request.method == 'POST':
        form = crearServicioForm(request.POST)
        if form.is_valid():
            # Aquí puedes simular la actualización del servicio
            servicio["nombre"] = form.cleaned_data['nombreServicio']
            servicio["descripcion"] = form.cleaned_data['descripcionServicio']
            servicio["precio"] = form.cleaned_data['precioServicio']
            return redirect('mostrarServicios')  # Redirige a la lista de servicios (deberás definir esta vista)
    else:
        form = crearServicioForm(initial={
            'nombreServicio': servicio['nombre'],
            'descripcionServicio': servicio['descripcion'],
            'precioServicio': servicio['precio'],
        })

    return render(request, 'MainApp/editar_servicio.html', {'form': form, 'service_id': service_id})