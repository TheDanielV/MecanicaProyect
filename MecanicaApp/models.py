from django.db import models


# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=30, default="Daniel")
    ci = models.CharField(max_length=30, primary_key=True, default=1)

    class Meta:
        abstract = True


class Vehicle(models.Model):
    placa = models.CharField(max_length=30,  primary_key=True)


class Station(models.Model):
    station_name = models.CharField(max_length=30)


class Employee(Person):
    station_assigned = models.OneToOneField(Station, on_delete=models.CASCADE, null=False, blank=False)


class Customer(Person):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, null=False, blank=False)
