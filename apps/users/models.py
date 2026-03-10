from datetime import datetime

from django.contrib.auth.hashers import check_password, make_password
from mongoengine import BooleanField, DateTimeField, Document, EmailField, StringField


class User(Document):
    ROLE_CUSTOMER = "customer"
    ROLE_STAFF = "staff"
    ROLE_ADMIN = "admin"
    ROLES = (ROLE_CUSTOMER, ROLE_STAFF, ROLE_ADMIN)

    name = StringField(required=True, max_length=120)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    phone = StringField(required=True, max_length=20)
    image = StringField(default="")
    role = StringField(required=True, choices=ROLES, default=ROLE_CUSTOMER)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "users",
        "indexes": ["email", "role", "created_at"],
    }

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_staff(self):
        return self.role in {self.ROLE_STAFF, self.ROLE_ADMIN}

    @property
    def is_superuser(self):
        return self.role == self.ROLE_ADMIN

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def profile_image(self):
        return self.image

    @profile_image.setter
    def profile_image(self, value):
        self.image = value

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)