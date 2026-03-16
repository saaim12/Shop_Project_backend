from datetime import datetime

from mongoengine import DateTimeField, Document, GenericReferenceField, IntField, ReferenceField, StringField

from apps.users.models import User


class Inventory(Document):
    CATEGORY_TYRE = "tyre"
    CATEGORY_SPARE_PART = "sparepart"
    CATEGORY_RIMS = "rims"
    CATEGORY_CARS = "cars"
    CATEGORY_CHOICES = [CATEGORY_TYRE, CATEGORY_SPARE_PART, CATEGORY_RIMS, CATEGORY_CARS]

    category = StringField(required=True, choices=CATEGORY_CHOICES)
    product = GenericReferenceField(required=True)
    quantity = IntField(required=True, min_value=0)
    storage_position = StringField(required=True, default="")
    stored_by = ReferenceField(User, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "inventory",
        "indexes": ["category", "stored_by", "quantity", "storage_position", "created_at", ("category", "stored_by")],
    }

    def save(self, *args, **kwargs):
        self.category = (self.category or "").strip().lower()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
