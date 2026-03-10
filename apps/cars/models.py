from datetime import datetime

from mongoengine import DateTimeField, Document, IntField, ListField, ReferenceField, StringField

from apps.users.models import User


class Car(Document):
    number_plate = StringField(required=True, unique=True, max_length=20)
    color = StringField(required=True, max_length=50)
    brand = StringField(required=True, max_length=100)
    model = StringField(required=True, max_length=100)
    year = IntField(required=True, min_value=1900)
    images = ListField(StringField(), default=list)
    created_by = ReferenceField(User, required=True)

    # Legacy field kept for backward compatibility with older documents.
    image = StringField(default="")

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "cars",
        "indexes": ["number_plate", "brand", "model", "year", "created_at"],
    }
