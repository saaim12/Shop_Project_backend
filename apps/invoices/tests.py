"""Invoices tests."""

from django.test import TestCase

from .models import Invoice


class InvoiceTestCase(TestCase):
    def test_invoice_status_choices(self):
        self.assertIn("paid", [choice[0] for choice in Invoice.Status.choices])
        self.assertIn("issued", [choice[0] for choice in Invoice.Status.choices])
