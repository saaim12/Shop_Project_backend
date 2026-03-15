from datetime import datetime
from datetime import timezone

from mongoengine import DateTimeField, Document, IntField, ReferenceField, StringField


class Car(Document):
    CONDITION_NEW = "NEW"
    CONDITION_USED = "USED"
    CONDITION_REFURBISHED = "REFURBISHED"
    CONDITION_CHOICES = [CONDITION_NEW, CONDITION_USED, CONDITION_REFURBISHED]

    name = StringField(required=True, max_length=150)
    brand = StringField(required=True, max_length=120)
    model = StringField(required=True, max_length=120)
    number_plate = StringField(required=False, unique=True, max_length=120, null=True)
    model_year = IntField(required=True, min_value=1951)
    year = IntField(required=True, min_value=1900)
    condition = StringField(required=True, choices=CONDITION_CHOICES)
    chassis_number = StringField(required=True, unique=True, max_length=120)
    description = StringField(default="")
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "cars",
        "indexes": ["name", "year", "brand", "model", "model_year", "chassis_number", "condition", "created_at"],
    }

    def save(self, *args, **kwargs):
        self.condition = (self.condition or "").upper()
        if not (self.number_plate or "").strip():
            self.number_plate = self.chassis_number
        current_year = datetime.now(timezone.utc).year
        if self.model_year and (self.model_year <= 1950 or self.model_year > current_year):
            raise ValueError("model_year must be greater than 1950 and less than or equal to current year")
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class CarImage(Document):
    car = ReferenceField(Car, required=True)
    image = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "car_images",
        "indexes": ["car", "created_at"],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
