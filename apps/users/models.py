from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django_mongodb_backend.fields import ObjectIdAutoField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email must be provided")

        if not password:
            raise ValueError("Password must be provided")

        email = self.normalize_email(email)

        if self.model.objects.filter(email=email).exists():
            raise ValueError("User with this email already exists")

        user_type = extra_fields.get("user_type", "customer")

        # staff automatically gets is_staff
        if user_type == "staff":
            extra_fields.setdefault("is_staff", True)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.full_clean()   # enforce model restrictions
        user.save(using=self._db)

        return user


    def create_superuser(self, email, password=None, key=None, **extra_fields):

        if key != settings.SECRET_KEY_FOR_ADMIN_USER:
            raise ValueError("Invalid admin creation key")

        extra_fields.setdefault("user_type", "staff")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email=email, password=password, **extra_fields)


    def delete_user(self, user_id):

        user = self.filter(id=user_id).first()

        if not user:
            raise ValueError("User not found")

        user.delete()
        return True


class User(AbstractBaseUser):

    id = ObjectIdAutoField(primary_key=True)

    USER_TYPES = [
        ("customer", "Customer"),
        ("staff", "Staff"),
    ]

    PHONE_VALIDATOR = RegexValidator(
        regex=r"^\+?[0-9]{7,15}$",
        message="Phone number must contain 7-15 digits and may start with +."
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[PHONE_VALIDATOR]
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default="customer"
    )

    age = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(18, message="Users must be at least 18 years old.")]
    )

    image = models.URLField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def clean(self):
        errors = {}

        if not self.email:
            errors["email"] = "Email is required."

        if self.is_superuser and not self.is_staff:
            errors["is_superuser"] = "Superuser must also be staff."

        if self.is_staff and self.user_type != "staff":
            errors["user_type"] = "Staff must have user_type='staff'."

        if self.user_type == "customer" and self.is_staff:
            errors["user_type"] = "Customer cannot be staff."

        if not self.phone:
            errors["phone"] = "Phone number is required."

        if self.age is None:
            errors["age"] = "Age is required."
        elif self.age < 18:
            errors["age"] = "Users must be at least 18 years old."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.email