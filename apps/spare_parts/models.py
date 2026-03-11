from datetime import datetime

from mongoengine import DateTimeField, Document, FloatField, ListField, ReferenceField, StringField

from apps.cars.models import Car
from apps.users.models import User


class SparePart(Document):
    CONDITION_NEW = "new"
    CONDITION_USED = "used"
    CONDITION_EXTERNAL = "external"

    CATEGORY_ENGINE = "engine"
    CATEGORY_ELECTRICAL = "electrical"
    CATEGORY_BODY = "body"
    CATEGORY_SUSPENSION = "suspension"
    CATEGORY_BRAKES = "brakes"
    CATEGORY_HEADLIGHTS = "headlights"
    CATEGORY_FILTER = "filter"
    CATEGORY_OTHER = "other"
    CATEGORY_CHOICES = [
        CATEGORY_ENGINE,
        CATEGORY_ELECTRICAL,
        CATEGORY_BODY,
        CATEGORY_SUSPENSION,
        CATEGORY_BRAKES,
        CATEGORY_HEADLIGHTS,
        CATEGORY_FILTER,
        CATEGORY_OTHER,
    ]

    name = StringField(required=True, max_length=120)
    description = StringField(default="")
    category = StringField(required=True, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
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
            "category",
            "condition",
            "car",
            "created_by",
            "created_at",
        ],
    }
