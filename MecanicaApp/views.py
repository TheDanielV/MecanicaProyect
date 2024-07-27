import os
import string
import random
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from docutils.nodes import description
from pyzbar.pyzbar import decode
from .forms import *
from django.shortcuts import render, redirect
from .forms import registerForm, loginForm, crearServicioForm
from services.AuthService.models import *
from .utils import *
from .models import *
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from MecanicaApp.decorators import *
from django.shortcuts import render, get_object_or_404, redirect

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
                try:
                    persona = Employee.objects.get(token=request.session.get('token'))
                except Employee.DoesNotExist:
                    pass
        if persona.role == 'admin':
            return redirect("listar_ordenes")
        elif persona.role == 'customer':
            return redirect("mostrarAutos")
        elif persona.role == 'employee':
            return redirect('mostrarEstacion')


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
        services = Service.get_services()
        return render(request, 'MainApp/orderServicio.html', context={'vechicle': vehicle, 'services': services})
    else:
        return redirect('mostrarAutos')


@role_login_required(allowed_roles=['customer'])
def generate_order(request):
    if request.method == 'POST':
        vehicle = Vehicle.get_vehicle_by_placa(request.POST.get('placa'))
        if vehicle.customer.token == request.session.get('token'):
            customer = Customer.get_customer(request.session.get('token'))
            services = Service.get_service_list_by_names(request.POST.getlist('servicios'))
            order = Order()
            order.generate_order(customer, vehicle, services)
            return redirect('mostrarAutos')
        else:
            return redirect('mostrarAutos')
    else:
        redirect('default_view')


@role_login_required(allowed_roles=['admin'])
def listar_ordenes(request):
    ordenes = Order.get_orders()
    return render(request, 'MainApp/AdminViews/contentOrdenes.html', {'ordenes': ordenes})


@role_login_required(allowed_roles=['admin'])
def detalle_orden(request, id):
    orden = Order.get_order_by_id(id)
    valor_total = 0
    return render(request, 'MainApp/AdminViews/contentDetalleOrden.html',
                  {'orden': orden, 'servicios': orden.service.all(), 'valor_total': valor_total})


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
    return render(request, 'MainApp/AdminViews/contentDetalleOrden.html',
                  {'orden': orden, 'servicios': servicios, 'valor_total': valor_total})


@role_login_required(allowed_roles=['customer'])
def payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            metodo_pago = form.cleaned_data['metodo_pago']
            if metodo_pago == 'transferencia':
                return redirect('transferencia')
            else:
                return redirect('success')

    else:
        form = PaymentForm()
    return render(request, 'MainApp/contentPayment.html', {'form': form})


@role_login_required(allowed_roles=['customer'])
def transferencia(request):
    if request.method == 'POST':
        form = TransferenciaForm(request.POST, request.FILES)
        if form.is_valid():
            return redirect('success')
    else:
        form = TransferenciaForm()
    return render(request, 'MainApp/contentTransferencia.html', {'form': form})


@role_login_required(allowed_roles=['customer'])
def retirarAuto(request):
    if request.method == 'POST':
        form = retirarAutoForm(request.POST, request.FILES)
        if form.is_valid():
            # Procesa los datos del formulario aquí, por ejemplo, guardándolos en la base de datos
            # name = form.cleaned_data['name']
            # last_name = form.cleaned_data['last_name']
            # cellphone = form.cleaned_data['cellphone']
            # ci = form.cleaned_data['ci']
            # file = form.cleaned_data['file']
            # Redirige a una página de éxito
            return redirect('success')
    else:
        form = retirarAutoForm()
    return render(request, 'MainApp/contentRetirarAuto.html', {'form': form})


def success(request):
    return render(request, 'MainApp/success.html')


def subirQR(request):
    if request.method == 'POST':
        form = QRCodeForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['qr_code']
            try:
                img = Image.open(image)
                decoded_objects = decode(img)
                qr_content = [obj.data.decode('utf-8') for obj in decoded_objects]
                print(qr_content)
                return render(request, 'QR/result.html', {'data': qr_content})
            except (IOError, ValueError) as e:
                return render(request, 'AuthViews/login.html', {'error': str(e)})
    else:
        form = QRCodeForm()
        return render(request, 'MainApp/subirQR.html', {'form': form})


@role_login_required(allowed_roles=['admin'])
def mostrar_servicios(request):
    services = Service.get_services()
    context = {
        'services': services
    }
    return render(request, 'MainApp/AdminViews/contentServices.html', context)


@role_login_required(allowed_roles=['admin'])
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
    return render(request, 'MainApp/AdminViews/crear_servicio.html', {'form': form})


@role_login_required(allowed_roles=['admin'])
def editarServicios(request, service_name):
    servicio = Service.get_service_by_name(service_name=service_name)
    if request.method == 'POST':
        form = crearServicioForm(request.POST)
        if form.is_valid():
            # Aquí puedes simular la actualización del servicio
            servicio.name = form.cleaned_data['nombreServicio']
            servicio.description = form.cleaned_data['descripcionServicio']
            # TODO agregar precio
            # servicio["precio"] = form.cleaned_data['precioServicio']
            return redirect('mostrarServicios')  # Redirige a la lista de servicios (deberás definir esta vista)
    else:
        form = crearServicioForm(initial={
            'nombreServicio': servicio.name,
            'descripcionServicio': servicio.description,
            'precioServicio': 0,
        })

    return render(request, 'MainApp/AdminViews/editar_servicio.html', {'form': form, 'service_id': service_name})


@role_login_required(['admin'])
def agregar_empleado(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        estacion_name = request.POST.get('estacion')
        email = request.POST.get('email')

        try:
            user = AuthUser()
            employee = Employee()
            password_char = string.ascii_letters + string.digits
            password = ''.join(random.choice(password_char) for _ in range(8))

            while not (any(c.isupper() for c in password) and any(c.isdigit() for c in password)):
                password = ''.join(random.choice(password_char) for _ in range(8))

            username = "emp" + nombre + apellido

            token = user.create_user(username, password, email)
            employee.create_employee(nombre, apellido, token, Station.get_station_by_name(estacion_name))
            # 4 Transaction
            with transaction.atomic(using=AUTH_DATABASE):
                user.save()
                with transaction.atomic(using='default'):
                    employee.save()
                    send_credentias_email(email, username, password)
        except IntegrityError as e:
            return render(request, 'MainApp/AdminViews/registratEmpleado.html', {'error': e})
        except InvalidPassword as e:
            return render(request, 'MainApp/AdminViews/registratEmpleado.html', {'error': e})

        return redirect('listar_ordenes')
    else:
        estaciones = Station.get_stations()
        return render(request, 'MainApp/AdminViews/registratEmpleado.html', {'estaciones': estaciones})
