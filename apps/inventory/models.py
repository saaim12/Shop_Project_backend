from datetime import datetime

from mongoengine import DateTimeField, Document, IntField, ReferenceField, StringField

from apps.spare_parts.models import SparePart
from apps.users.models import User


class Inventory(Document):
    spare_part = ReferenceField(SparePart, required=True)
    quantity = IntField(required=True, min_value=0)
    storage_position = StringField(default="")
    added_by = ReferenceField(User, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "inventory",
        "indexes": ["spare_part", "quantity", "storage_position", "created_at"],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
