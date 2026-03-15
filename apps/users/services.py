from django.conf import settings

from apps.services.s3_service import S3Service
from apps.users.models import User


class UserService:

    @staticmethod
    def create_user(payload, actor_user=None):

        role = payload.get("role", "CUSTOMER").upper()
        provided_key = (payload.get("key") or "").strip()
        actor_role = (getattr(actor_user, "role", "") or "").upper()

        # CUSTOMER must register themselves
        if role == "CUSTOMER":
            if actor_user and getattr(actor_user, "is_authenticated", False):
                raise ValueError("Admin cannot create customer users")

        if role == "STAFF":
            if not actor_user or actor_role != "ADMIN":
                raise ValueError("Only admin can create STAFF")

            expected_key = (settings.SECRET_KEY_FOR_STAFF_USER or "").strip()
            if not expected_key:
                raise ValueError("Staff creation key is not configured")
            if provided_key != expected_key:
                raise ValueError("Invalid staff creation key")

        if role == "ADMIN":
            expected_key = (settings.SECRET_KEY_FOR_ADMIN_USER or "").strip()
            if not expected_key:
                raise ValueError("Admin creation key is not configured")
            if provided_key != expected_key:
                raise ValueError("Invalid admin creation key")

        user = User(
            name=payload["name"],
            email=payload["email"],
            age=payload["age"],
            phone_number=payload["phone_number"],
            image=(payload.get("image") or "").strip(),
            role=role,
        )

        user.set_password(payload["password"])

        user.save()

        return user

    @staticmethod
    def update_user(user, payload):

        for field in ["name", "email", "age", "phone_number", "image", "role"]:

            if field in payload:
                if field == "email":
                    email = (payload[field] or "").strip().lower()
                    existing = User.objects(email=email).first()
                    if existing and str(existing.id) != str(user.id):
                        raise ValueError("Email already exists")
                    setattr(user, field, email)
                    continue
                if field == "image":
                    setattr(user, field, (payload[field] or "").strip())
                    continue
                if field == "role":
                    role = (payload[field] or "").strip().upper()
                    if role not in {"CUSTOMER", "STAFF", "ADMIN"}:
                        raise ValueError("Invalid role")
                    setattr(user, field, role)
                    continue
                setattr(user, field, payload[field])

        if "old_password" in payload and "new_password" in payload:
            if not user.check_password(payload["old_password"]):
                raise ValueError("Incorrect current password")
            user.set_password(payload["new_password"])

        user.save()

        return user

    @staticmethod
    def delete_user(request_user, target_user):

        request_role = (getattr(request_user, "role", "") or "").upper()
        is_admin = request_role == "ADMIN"
        is_self = str(getattr(request_user, "id", "")) == str(getattr(target_user, "id", ""))

        if not is_admin and not is_self:
            raise ValueError("Only admin can delete other users")

        image_url = (getattr(target_user, "image", "") or "").strip()
        if image_url:
            try:
                S3Service().delete_image(image_url)
            except Exception:
                pass

        target_user.delete()