from enum import Enum

from django.db import models
from .utils import *
from typing import List


# Create your models here.
class Person(models.Model):
    class Role(Enum):
        CUSTOMER = 'customer'
        EMPLOYEE = 'employee'
        ADMIN = 'admin'

    name = models.CharField(max_length=30, default="None")
    last_name = models.CharField(max_length=30, null=False, default="None")
    role = models.CharField(max_length=100, choices=[(tag.name, tag.value) for tag in Role],
                            default=Role.CUSTOMER.value)
    token = models.CharField(max_length=100, null=False, unique=True, default="00000")

    class Meta:
        abstract = True


class Customer(Person):
    ci = models.CharField(max_length=255, unique=True, default="0000000000")
    cellphone = models.CharField(max_length=255, default="0000000000")
    direction = models.CharField(max_length=255, default="None")

    def create(self, name, last_name, ci, cellphone, direction, token):
        self.name = name
        self.token = token
        self.last_name = last_name
        self.ci = encrypt_data(ci)
        self.cellphone = encrypt_data(cellphone)
        self.direction = encrypt_data(direction)
        self.role = Person.Role.CUSTOMER.value

    @staticmethod
    def get_customer(token):
        customer_enc = Customer.objects.get(token=token)
        customer_dec = customer_enc
        customer_dec.ci = decrypt_data(customer_enc.ci)
        customer_dec.cellphone = decrypt_data(customer_enc.cellphone)
        customer_dec.direction = decrypt_data(customer_enc.direction)

        return customer_dec


class Guest(models.Model):
    ci = models.CharField(max_length=20, primary_key=True, default="0000000000")
    name = models.CharField(max_length=30, default="None")
    last_name = models.CharField(max_length=30, null=False, default="None")
    validation_token = models.CharField(max_length=50, default=None)
    file = models.FileField(upload_to='files/')
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    def create_guest(self, ci, name, last_name, validation_token):
        self.ci = ci
        self.name = name
        self.last_name = last_name
        self.validation_token = validation_token
        self.save()


class Vehicle(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='vehicles', default="0000000000")
    marca = models.CharField(max_length=255, default=None)
    model = models.CharField(max_length=255, default=None)
    placa = models.CharField(max_length=255, default=None)
    anio = models.CharField(max_length=30, default=None)
    color = models.CharField(max_length=30, default=None)

    def create_auto(self, customer, marca, model, placa, anio, color):
        self.customer = customer
        self.marca = marca
        self.model = model
        self.placa = encrypt_data(placa)
        self.anio = anio
        self.color = color

    @staticmethod
    def get_vehicle_by_placa(placa):
        vehivle_ced = Vehicle.objects.get(pk=placa)
        vehivle_ced.placa = decrypt_data(vehivle_ced.placa)
        return vehivle_ced

    class Meta:
        db_table = 'mecanicaapp_vehicle'

    @staticmethod
    def delete_vehicle(placa):
        Vehicle.objects.get(placa=encrypt_data(placa)).delete()

    @classmethod
    def get_vehicle_by_customer(cls, token):
        vehicles = Vehicle.objects.filter(customer__token=token)
        for vehicle in vehicles:
            vehicle.placa = decrypt_data(vehicle.placa)
            print(vehicle.placa)


        return vehicles

class Admin(Person):
    def create_admin(self, name, last_name, token):
        self.name = name
        self.last_name = last_name
        self.role = Person.Role.ADMIN.value
        self.token = token
        self.save()


class Station(models.Model):
    station_name = models.CharField(max_length=30)

    def create_station(self, station_name):
        """
        Crea una nueva estación y la guarda en la base de datos.

        Args:
            station_name (str): El nombre de la estación.

        Returns:
            Station: La instancia de la estación creada.
        """
        self.station_name = station_name
        self.save()
        return self

    @classmethod
    def get_station_by_name(cls, station_name):
        """
        Obtiene una estación por su nombre.

        Args:
            station_name (str): El nombre de la estación.

        Returns:
            Station: La instancia de la estación encontrada.
        """
        return cls.objects.get(station_name=station_name)

    @classmethod
    def get_stations(cls):
        return cls.objects.all()

    @classmethod
    def get_station_by_id(cls, station_id):
        return cls.objects.get(pk=station_id)

    def __str__(self):
        return self.station_name


class Employee(Person):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='employees')

    def create_employee(self, name, last_name, token, station):
        self.name = name
        self.last_name = last_name
        self.role = Person.Role.EMPLOYEE.value
        self.token = token
        self.station = station

    @classmethod
    def get_employee(cls, token):
        return cls.objects.get(token=token)


class Service(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def create_service(self, station, name, description, price):
        """
        Crea un nuevo servicio asociado a una estación.

        Este método asigna los valores proporcionados a los atributos del servicio y guarda el objeto en la base de datos.

        Args:
            station (Station): La estación con la que se asocia el servicio.
            name (str): El nombre del servicio.
            description (str): Una breve descripción del servicio.
            price(double): Precio del servicio

        Returns:
            Service: La instancia del servicio creado.
        """
        self.station = station
        self.name = name
        self.description = description
        self.price = price
        self.save()
        return self

    @classmethod
    def get_service_by_name(cls, service_id):
        """
        Obtiene un servicio por su Nombre.

        Args:
            service_id (str): El ID del servicio.

        Returns:
            Service: La instancia del servicio encontrado.
        """
        return cls.objects.get(pk=service_id)

    @classmethod
    def get_services(cls):
        return cls.objects.all()

    def update_service(self):
        self.save()

    @classmethod
    def get_service_list_by_names(cls, services_raw):
        return cls.objects.filter(name__in=services_raw)

    @classmethod
    def delete_service(cls, id):
        servicio = cls.objects.get(pk=id)
        servicio.delete()


class Order(models.Model):
    PAGADO = 'pagado'
    ESTADO_FINALIZADO = 'finalizado'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='ordenes')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='ordenes')
    service = models.ManyToManyField(Service)
    state = models.CharField(max_length=255, default=None)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    #  payment = models.CharField(max_length=2, choices=METODO_PAGO_CHOICES)

    def generate_order(self, customer, vehicle, services):
        self.customer = customer
        self.vehicle = vehicle
        self.state = services[0].station.station_name
        self.save()
        self.service.set(services)
        self.total = 0
        for service in services:
            self.total = self.total + service.price
        self.save()

    @classmethod
    def get_orders(cls):
        orders = cls.objects.all()
        for order in orders:
            order.vehicle.placa=decrypt_data(order.vehicle.placa)
        return orders

    def __str__(self):
        return f'Orden de {self.customer.name} para {self.vehicle.placa}'

    @classmethod
    def get_order_by_id(cls, order_id):
        dec_order = cls.objects.get(id=order_id)
        dec_order.vehicle.placa = decrypt_data(dec_order.vehicle.placa)
        return dec_order

    @classmethod
    def get_station_dto(cls, station_id):
        servicios_en_estacion = []
        dto_list = []
        orders = cls.objects.exclude(state=cls.ESTADO_FINALIZADO)
        for order in orders:
            order.vehicle.placa = decrypt_data(order.vehicle.placa)
            for service in order.service.all():
                if service.station.id == station_id and order.state == Station.get_station_by_id(
                        station_id).station_name:
                    servicios_en_estacion.append(service)
                    placa = order.vehicle.placa
                    dto_list.append(StationDTO(order.id, placa, service))
        return dto_list

    @classmethod
    def get_station_dto_by_order_id(cls, order_id):
        order = cls.get_order_by_id(order_id)
        dto = StationDTO(order_id, order.vehicle.placa, order.service)
        return dto

    @classmethod
    def update_state(cls, station_id, station_name):
        order = cls.objects.get(id=station_id)

        servicios = order.service.all()
        current_station = order.state

        # Encontrar el siguiente servicio con una estación diferente
        next_service = None
        for service in servicios:
            if service.station.station_name != current_station:
                next_service = service
                break

        if next_service:
            print('se actualiza')
            order.state = next_service.station.station_name
        else:
            print('se finaliza')
            order.state = "finalizado"

        order.save()

    @classmethod
    def get_orders_by_client(cls, customer):
        """
        Obtiene todas las órdenes asociadas a un cliente específico.

        Args:
            customer (Customer): El cliente cuyas órdenes se desean obtener.

        Returns:
            QuerySet: Un QuerySet con las órdenes del cliente.
        """
        orders = cls.objects.filter(customer=customer)
        decrypt_orders = []
        for order in orders.all():
            order.vehicle.placa = decrypt_data(order.vehicle.placa)
            decrypt_orders.append(order)
        return decrypt_orders

    @classmethod
    def get_order_by_id_and_customer(cls, id, customer):
        dec_order = cls.objects.get(customer=customer, id=id)
        dec_order.vehicle.placa = decrypt_data(dec_order.vehicle.placa)
        return dec_order


class Payment(models.Model):
    TIPO_TRANSFERENCIA = 'transferencia'
    TIPO_VENTANILLA = 'ventanilla'
    TIPO_PAGO_CHOICES = [
        (TIPO_TRANSFERENCIA, 'Transferencia'),
        (TIPO_VENTANILLA, 'Pago en ventanilla'),
    ]

    ESTADO_EN_PROCESO = 'en proceso'
    ESTADO_EN_ESPERA = 'en espera'
    ESTADO_PAGADO = 'pagado'
    ESTADO_PAGO_CHOICES = [
        (ESTADO_EN_PROCESO, 'En proceso'),
        (ESTADO_EN_ESPERA, 'En espera'),
        (ESTADO_EN_ESPERA, 'Pagado'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='pagos', primary_key=True)
    tipo = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default=ESTADO_EN_ESPERA)
    imagen_transferencia = models.BinaryField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.tipo == self.TIPO_TRANSFERENCIA:
            self.estado = self.ESTADO_EN_PROCESO
        else:
            self.estado = self.ESTADO_PAGADO
        super().save(*args, **kwargs)


class StationDTO:
    def __init__(self, order_id, placa, service):
        self.order_id = order_id
        self.placa = placa
        self.service = service
