from datetime import datetime

from mongoengine import DateTimeField, Document, IntField, ReferenceField

from apps.spare_parts.models import SparePart
from apps.users.models import User


class Inventory(Document):
    spare_part = ReferenceField(SparePart, required=True, unique=True)
    quantity = IntField(required=True, min_value=0)
    updated_by = ReferenceField(User, required=True)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "inventory",
        "indexes": ["spare_part", "updated_at"],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
