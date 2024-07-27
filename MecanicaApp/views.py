import os

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from services.AuthService.models import *
from .utils import *
from .models import *
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from MecanicaApp.decorators import *

AUTH_DATABASE = 'auth_db'
LOG_DATABASE = 'log_db'


def index(request):
    title = "MecanicaApp"
    client_ip = request.META.get('REMOTE_ADDR')
    print(client_ip)
    if request.session.get('token') is not None:
        return redirect('default_view')
    else:
        return render(request, 'index.html', {
            'title': title
        })


@role_login_required(allowed_roles=['admin', 'employee', 'customer'])
def default_view(request):
    if request.session.get('token') is not None:

        persona = None
        try:
            persona = Customer.objects.get(token=request.session.get('token'))
        except Customer.DoesNotExist:
            try:
                persona = Admin.objects.get(token=request.session.get('token'))
            except Admin.DoesNotExist:
                pass
        if persona.role == 'admin':
            return redirect("listar_ordenes")
        elif persona.role == 'customer':
            return redirect("mostrarAutos")


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
                # 4 Transaction

                with transaction.atomic(using=AUTH_DATABASE):
                    user.save()
                    with transaction.atomic(using='default'):
                        customer.save()

            except IntegrityError as e:
                # voy a reenviar el mismo formulario con los datos mismos datos, excepto contraseña
                return render(request, 'AuthViews/register.html', {'form': form, 'error': e})
            except InvalidPassword as e:
                return render(request, 'AuthViews/register.html', {'form': form, 'error': e})

            # en caso de no ocurrir ningun error
            return render(request, 'index.html', {
                'title': "Usuario Creado"
            })
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
            if auth_key is not None:
                request.session['token'] = auth_key
                # Redirección en base a roles
                return redirect('default_view')

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


@role_login_required(allowed_roles=['customer'])
def ordenar_servicio(request, id):
    vehicle = Vehicle.get_vehicle_by_placa(id)
    if vehicle.customer.token == request.session.get('token'):
        return render(request, 'MainApp/orderServicio.html', context={'vechicle': vehicle})
    else:
        return redirect('mostrarAutos')


@role_login_required(allowed_roles=['admin'])
def listar_ordenes(request):
    ordenes = [
        {
            'id': 1,
            'cliente': {'nombre': 'Juan Pérez'},
            'placa': 'PCM-6769',
            'valor_total': 15000,
            'estado': 'Pagado'
        },
        {
            'id': 2,
            'cliente': {'nombre': 'Ana López'},
            'placa': 'PDB-1856',
            'valor_total': 18000,
            'estado': 'No Pagado'
        },
        {
            'id': 3,
            'cliente': {'nombre': 'Luis Martínez'},
            'placa': 'PBB-1412',
            'valor_total': 20000,
            'estado': 'Pagado'
        }
    ]
    return render(request, 'MainApp/contentOrdenes.html', {'ordenes': ordenes})


@role_login_required(allowed_roles=['admin'])
def detalle_orden(request, id):
    orden = {
        'id': id,
        'fecha': '2023-07-10',
        'cliente': {'nombre': 'Juan Pérez'},
        'vehiculo': 'PCM-6769'
    }
    servicios = [
        {
            'codigo': 1,
            'descripcion': 'Cambio de aceite',
            'total': 50.00
        },
        {
            'codigo': 2,
            'descripcion': 'Revisión de frenos',
            'total': 30.00
        }
    ]
    valor_total = sum(servicio['total'] for servicio in servicios)
    return render(request, 'MainApp/contentDetalleOrden.html',
                  {'orden': orden, 'servicios': servicios, 'valor_total': valor_total})


def upload_qr(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST, request.FILES)
        if form.is_valid():
            qr_image = form.cleaned_data['qr_code']
            qr_image_bytes = BytesIO(qr_image.read())

            # decrypted_data = read_qr_code(qr_image_bytes)
            # obj_dict = json.loads(decrypted_data) if decrypted_data else None

            return render(request, 'QR/result.html', {'data': "n"})

    else:
        form = QRCodeForm()
    return render(request, 'QR/upload_qr.html', {'form': form})


def create_admin(request):
    auth = AuthUser()
    token = auth.create_user(password="Password1020", username='Admin', email='admin@admin.com')
    auth.save()
    admin = Admin()
    admin.create_admin("daniel", "vargas", token)
    admin.save()
    return redirect('login')
