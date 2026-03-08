"""Parts models."""

from django.db import models


class PartCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Part Categories"

    def __str__(self):
        return self.name


class Part(models.Model):
    category = models.ForeignKey(
        PartCategory, on_delete=models.CASCADE, related_name="parts"
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parts",
    )
    name = models.CharField(max_length=200)
    part_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    location = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="parts/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level

    def __str__(self):
        return f"{self.part_number} – {self.name}"


class StockAdjustment(models.Model):
    class AdjustmentType(models.TextChoices):
        PURCHASE = "purchase", "Purchase"
        SALE = "sale", "Sale"
        RETURN = "return", "Return"
        DAMAGE = "damage", "Damage"
        CORRECTION = "correction", "Correction"

    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="adjustments")
    adjustment_type = models.CharField(max_length=20, choices=AdjustmentType.choices)
    quantity = models.IntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.adjustment_type} | {self.part} | qty={self.quantity}"
