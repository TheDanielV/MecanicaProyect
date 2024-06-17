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

    class Meta:
        abstract = True


class Customer(Person):
    ci = models.CharField(max_length=20, primary_key=True, default="0000000000")
    cellphone = models.CharField(max_length=20, default="0000000000")
    direction = models.CharField(max_length=255, default="None")


class Vehicle(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='vehicles', default="0000000000")
    marca = models.CharField(max_length=255, default=None)
    model = models.CharField(max_length=255, default=None)
    placa = models.CharField(max_length=30, default=None)


class Admin(Person):
    order = models.CharField(max_length=255, default=None)


class Station(models.Model):
    station_name = models.CharField(max_length=30)


class Employee(Person):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='employees')
