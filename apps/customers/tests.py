"""Customers tests."""

from django.test import TestCase

from .models import Customer


class CustomerTestCase(TestCase):
    def test_customer_full_name(self):
        customer = Customer(first_name="John", last_name="Doe", email="john@example.com", phone="555-1234")
        self.assertEqual(customer.full_name, "John Doe")
