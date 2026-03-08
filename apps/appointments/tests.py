"""Appointments tests."""

from django.test import TestCase

from apps.customers.models import Customer


class AppointmentTestCase(TestCase):
    def test_customer_created_for_appointment_fixture(self):
        customer = Customer.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="555-9876",
        )
        self.assertEqual(customer.full_name, "Jane Smith")
