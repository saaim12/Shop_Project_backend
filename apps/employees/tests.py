"""Employees tests."""

from django.test import TestCase

from .models import Department


class EmployeeTestCase(TestCase):
    def test_department_creation(self):
        dept = Department.objects.create(name="Service Bay")
        self.assertEqual(str(dept), "Service Bay")
