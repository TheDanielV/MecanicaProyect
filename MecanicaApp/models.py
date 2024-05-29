from django.db import models


# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=30)
    ci = models.CharField(max_length=30)


class Vehicle(models.Model):
    placa = models.CharField(max_length=30)


class Station(models.Model):
    station_name = models.CharField(max_length=30)


class Employee(Person):
    station_assigned = Station()
