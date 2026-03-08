"""Services tests."""

from django.test import TestCase

from .models import ServiceCategory


class ServiceTestCase(TestCase):
    def test_service_category_creation(self):
        category = ServiceCategory.objects.create(name="Oil Change")
        self.assertEqual(str(category), "Oil Change")
