from datetime import datetime
from datetime import timezone

from mongoengine import DateTimeField, Document, IntField, ReferenceField, StringField


class SparePart(Document):
    CONDITION_NEW = "NEW"
    CONDITION_USED = "USED"
    CONDITION_REFURBISHED = "REFURBISHED"
    CONDITION_CHOICES = [CONDITION_NEW, CONDITION_USED, CONDITION_REFURBISHED]

    VEHICLE_CAR = "cars"
    VEHICLE_TRUCK = "trucks"
    VEHICLE_MOTORCYCLE = "motorcycles"
    VEHICLE_UNIVERSAL = "universal"
    VEHICLE_TYPE_CHOICES = [VEHICLE_CAR, VEHICLE_TRUCK, VEHICLE_MOTORCYCLE, VEHICLE_UNIVERSAL]

    CATEGORY_CHOICES = [
        "Axles / Rear axle / Front axle / Cardan shaft",
        "Trailer hitch",
        "Fuel system",
        "Brake system",
        "Tires / Rims",
        "Filters",
        "Sensor",
        "Gearbox",
        "Hybrid / Electric car",
        "Intake",
        "Instrument / Contact / Multimedia",
        "Interior / Upholstery",
        "Body / Sheet metal parts",
        "Clutch / Flywheel",
        "Cooling / Air conditioning / Heating system",
        "Locking system",
        "Lamp / Lighting",
        "Motor",
        "Engine parts",
        "Security system",
        "Mirror / Window",
        "Control unit / Wiring harness",
        "Steering",
        "Accessories",
        "Exhaust system",
        "Chassis / Suspension",
        "Wiper / Washer",
        "Trailer",
        "Lighting",
        "Instrument / Contacts",
        "Bodywork",
        "Pedals",
        "Mirrors / windows",
        "Control units / Wiring harness",
        "Chassis / suspension / mounts",
        "Electrical components",
        "Consumable parts",
        "Chemistry",
        "Bulbs",
        "Tools/Equipment",
        "Others",
    ]

    name = StringField(required=True, max_length=150)
    brand = StringField(required=True, max_length=120)
    model = StringField(required=True, max_length=120)
    model_year = IntField(required=True, min_value=1951)
    vehicle_type = StringField(required=True, choices=VEHICLE_TYPE_CHOICES)
    category = StringField(required=True, choices=CATEGORY_CHOICES)
    condition = StringField(required=True, choices=CONDITION_CHOICES)
    description = StringField(default="")
    item_number = StringField(default="")
    article_number = StringField(default="")
    ditto_number = StringField(default="")
    engine_code = StringField(default="")
    engine_spec = StringField(default="")
    chassis_number = StringField(default="")
    mileage = IntField(min_value=0, default=0)
    family_card_number = StringField(default="")
    oem_numbers = StringField(default="")
    identification_numbers = StringField(default="")
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "spare_parts",
        "indexes": [
            "name",
            "brand",
            "model",
            "vehicle_type",
            "category",
            "condition",
            "item_number",
            "engine_code",
            "oem_numbers",
            "created_at",
            ("brand", "model"),
            ("vehicle_type", "category"),
        ],
    }

    def save(self, *args, **kwargs):
        self.condition = (self.condition or "").upper()
        current_year = datetime.now(timezone.utc).year
        if self.model_year and (self.model_year <= 1950 or self.model_year > current_year):
            raise ValueError("model_year must be greater than 1950 and less than or equal to current year")
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class SparePartImage(Document):
    spare_part = ReferenceField(SparePart, required=True)
    image = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "spare_part_images",
        "indexes": ["spare_part", "created_at"],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
