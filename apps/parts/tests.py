"""Parts tests."""

from django.test import TestCase

from .models import PartCategory


class PartTestCase(TestCase):
    def test_part_category_creation(self):
        category = PartCategory.objects.create(name="Filters")
        self.assertEqual(str(category), "Filters")
