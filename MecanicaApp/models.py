from enum import Enum

from django.db import models


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
    ci = models.CharField(max_length=20, primary_key=True, default="0000000000")
    cellphone = models.CharField(max_length=20, default="0000000000")
    direction = models.CharField(max_length=255, default="None")

    def create(self, name, last_name, ci, cellphone, direction, token):

        self.name = name
        self.token = token
        self.last_name = last_name
        self.ci = ci
        self.cellphone = cellphone
        self.direction = direction
        self.role = Person.Role.CUSTOMER.value

    @staticmethod
    def get_customer(token):
        return Customer.objects.get(token=token)


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
    placa = models.CharField(max_length=30, default=None)
    anio = models.CharField(max_length=30, default=None)
    color = models.CharField(max_length=30, default=None)

    def create_auto(self, customer, marca, model, placa, anio, color):
        self.customer = customer
        self.marca = marca
        self.model = model
        self.placa = placa
        self.anio = anio
        self.color = color

    @staticmethod
    def get_vehicle_by_placa(placa):
        return Vehicle.objects.get(placa=placa)

    class Meta:
        db_table = 'mecanicaapp_vehicle'

    @staticmethod
    def delete_vehicle(placa):
        Vehicle.objects.get(placa=placa).delete()


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


class Employee(Person):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='employees')

    def create_employee(self, name, last_name, token, station):
        self.name = name
        self.last_name = last_name
        self.role = Person.Role.EMPLOYEE.value
        self.token = token
        self.station = station


class Service(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def create_service(self, station, name, description):
        """
        Crea un nuevo servicio asociado a una estación.

        Este método asigna los valores proporcionados a los atributos del servicio y guarda el objeto en la base de datos.

        Args:
            station (Station): La estación con la que se asocia el servicio.
            name (str): El nombre del servicio.
            description (str): Una breve descripción del servicio.

        Returns:
            Service: La instancia del servicio creado.
        """
        self.station = station
        self.name = name
        self.description = description
        self.save()
        return self

    @classmethod
    def get_service_by_name(cls, service_name):
        """
        Obtiene un servicio por su Nombre.

        Args:
            service_name (str): El Nombre del servicio.

        Returns:
            Service: La instancia del servicio encontrado.
        """
        return cls.objects.get(name=service_name)

    @classmethod
    def get_services(cls):
        return cls.objects.all()

    def update_service(self):
        self.save()

    @classmethod
    def get_service_list_by_names(cls, services_raw):
        return cls.objects.filter(name__in=services_raw)


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='ordenes')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='ordenes')
    service = models.ManyToManyField(Service)

    #  payment = models.CharField(max_length=2, choices=METODO_PAGO_CHOICES)

    def generate_order(self, customer, vehicle, services):

        self.customer = customer
        self.vehicle = vehicle
        self.save()
        self.service.set(services)
        self.save()



    @classmethod
    def get_orders(cls):
        return cls.objects.all()

    def __str__(self):
        return f'Orden de {self.customer.name} para {self.vehicle.placa}'

    @classmethod
    def get_order_by_id(cls, order_id):
        return cls.objects.get(id=order_id)


class Payment(models.Model):
    class State(Enum):
        IN_PROGRESS = 'in progress'
        ACCEPTED = 'accepted'
        REJECTED = 'rejected'

    state = models.CharField(max_length=100, choices=[(tag.name, tag.value) for tag in State],
                             default=State.IN_PROGRESS.value)

    class Meta:
        abstract = True


class Cash(Payment):
    evidence = models.CharField(max_length=30, null=False, default="None")


class BankCard(Payment):
    tokenized_pin = models.CharField(max_length=30, null=False, default="None")
    reference = models.CharField(max_length=30, null=False, default="None")
