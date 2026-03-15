from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from mongoengine import (
    Document,
    StringField,
    EmailField,
    IntField,
    BooleanField,
    DateTimeField,
)


class User(Document):

    ROLE_CUSTOMER = "CUSTOMER"
    ROLE_STAFF = "STAFF"
    ROLE_ADMIN = "ADMIN"

    ROLES = (ROLE_CUSTOMER, ROLE_STAFF, ROLE_ADMIN)

    name = StringField(required=True, max_length=120)

    email = EmailField(required=True, unique=True)

    age = IntField(required=True, min_value=18, max_value=90)

    password = StringField(required=True)

    phone_number = StringField(required=True, max_length=20)

    image = StringField(default="")

    role = StringField(required=True, choices=ROLES, default=ROLE_CUSTOMER)

    is_active = BooleanField(default=True)

    created_at = DateTimeField(default=datetime.utcnow)

    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "users",
        "indexes": ["name", "email", "role", "created_at"],
    }

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def save(self, *args, **kwargs):

        self.email = (self.email or "").lower().strip()
        self.role = (self.role or self.ROLE_CUSTOMER).upper()
        self.updated_at = datetime.utcnow()

        return super().save(*args, **kwargs)


class BlacklistedToken(Document):

    token_hash = StringField(required=True, unique=True)

    token_type = StringField(required=True, choices=("access", "refresh"), default="refresh")

    expires_at = DateTimeField(required=True)

    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "blacklisted_tokens",
        "indexes": [
            "token_hash",
            {"fields": ["expires_at"], "expireAfterSeconds": 0},
        ],
    }