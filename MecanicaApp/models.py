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



class Vehicle(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='vehicles', default="0000000000")
    marca = models.CharField(max_length=255, default=None)
    model = models.CharField(max_length=255, default=None)
    placa = models.CharField(max_length=30, default=None)

    def create(self, customer, marca, model, placa):
        self.customer = customer
        self.marca = marca
        self.model = model
        self.placa = placa

    @staticmethod
    def delete_vehicle(placa):
        Vehicle.objects.get(placa=placa).delete()


class Admin(Person):
    order = models.CharField(max_length=255, default=None)


class Station(models.Model):
    station_name = models.CharField(max_length=30)


class Employee(Person):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='employees')


class Service(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='servicios')
    name = models.CharField(max_length=255)
    description = models.TextField()


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='ordenes')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='ordenes')
    service = models.ManyToManyField(Service, related_name='ordenes')

    #  payment = models.CharField(max_length=2, choices=METODO_PAGO_CHOICES)

    def create(self, customer, vehicle):
        self.customer = customer
        self.vehicle = vehicle

    def __str__(self):
        return f'Orden de {self.customer.name} para {self.vehicle.placa}'
