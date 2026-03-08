"""Suppliers tests."""

from django.test import TestCase

from .models import Supplier


class SupplierTestCase(TestCase):
    def test_supplier_creation(self):
        supplier = Supplier.objects.create(name="AutoParts Inc.")
        self.assertEqual(str(supplier), "AutoParts Inc.")
