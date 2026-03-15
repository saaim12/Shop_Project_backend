from datetime import datetime

from mongoengine import DateTimeField, Document, FloatField, ReferenceField, StringField


class Tyre(Document):
    CONDITION_NEW = "NEW"
    CONDITION_USED = "USED"
    CONDITION_REFURBISHED = "REFURBISHED"
    CONDITION_CHOICES = [CONDITION_NEW, CONDITION_USED, CONDITION_REFURBISHED]

    company = StringField(required=True, max_length=120)
    condition = StringField(required=True, choices=CONDITION_CHOICES)
    inches = FloatField(required=True, min_value=1)
    type = StringField(required=True, max_length=120)
    description = StringField(default="")
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "tyres",
        "indexes": ["company", "condition", "inches", "type", "created_at"],
    }

    def save(self, *args, **kwargs):
        self.condition = (self.condition or "").upper()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class TyreImage(Document):
    tyre = ReferenceField(Tyre, required=True)
    image = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "tyre_images",
        "indexes": ["tyre", "created_at"],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
