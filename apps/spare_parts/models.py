from datetime import datetime

from mongoengine import DateTimeField, Document, FloatField, ListField, ReferenceField, StringField

from apps.cars.models import Car
from apps.users.models import User


class SparePart(Document):
    CONDITION_NEW = "new"
    CONDITION_USED = "used"
    CONDITION_EXTERNAL = "external"

    name = StringField(required=True, max_length=120)
    description = StringField(default="")
    price = FloatField(required=True, min_value=0)
    quantity = FloatField(required=True, min_value=1, default=1)
    condition = StringField(required=True, choices=[CONDITION_NEW, CONDITION_USED, CONDITION_EXTERNAL])
    images = ListField(StringField(), default=list)
    car = ReferenceField(Car, null=True)
    created_by = ReferenceField(User, required=True)

    # Legacy fields kept for backward compatibility with older documents.
    image = StringField(default="")
    car_reference = ReferenceField(Car, null=True)
    added_by = ReferenceField(User, null=True)

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "spare_parts",
        "indexes": [
            "condition",
            "car",
            "created_by",
            "created_at",
        ],
    }
