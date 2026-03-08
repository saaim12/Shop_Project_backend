"""Vehicles tests."""

from django.test import TestCase

from .models import Make


class VehicleTestCase(TestCase):
    def test_make_creation(self):
        make = Make.objects.create(name="Toyota")
        self.assertEqual(str(make), "Toyota")
