from datetime import datetime

from mongoengine import DateTimeField, Document, FloatField, IntField, ListField, ReferenceField, StringField

from apps.spare_parts.models import SparePart
from apps.users.models import User


class Order(Document):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"
    STATUSES = [STATUS_PENDING, STATUS_CONFIRMED, STATUS_CANCELLED, STATUS_COMPLETED]

    customer = ReferenceField(User, required=True)
    spare_part = ReferenceField(SparePart, null=True)
    quantity = IntField(required=True, min_value=1, default=1)
    spare_parts = ListField(ReferenceField(SparePart), required=True)
    total_price = FloatField(required=True, min_value=0)
    status = StringField(choices=STATUSES, default=STATUS_PENDING)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "orders",
        "indexes": ["customer", "spare_part", "status", "created_at"],
    }
