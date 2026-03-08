"""Orders tests."""

from django.test import TestCase

from apps.customers.models import Customer
from apps.vehicles.models import Make


class OrderTestCase(TestCase):
    def test_order_prerequisites(self):
        make = Make.objects.create(name="Honda")
        self.assertEqual(str(make), "Honda")
