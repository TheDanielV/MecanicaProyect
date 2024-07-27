import faker
from django.test import TestCase
from .models import *
from services.AuthService.models import *
from faker import Faker


# Create your tests here.

class OrderTestCase(TestCase):

    def test_data_creation(self):
        faker = Faker()
        customer = Customer()
        customer.create(faker.name(), faker.last_name(),
                        "000000000", "0000000000",
                        faker.address(), "00000000000000")
        vehicle = Vehicle()
        vehicle.create_auto(customer, "Susuki", "AAAAAA", "PNA0000")

        order = Order()
        order.create(customer, vehicle)
        self.assertEqual(customer.name, order.customer.name, "data created for an order")
        pass
