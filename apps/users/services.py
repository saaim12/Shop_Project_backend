from django.conf import settings

from apps.services.s3_service import S3Service
from apps.users.models import User


class UserService:

    @staticmethod
    def create_user(payload, image_file=None):
        email = payload["email"].strip().lower()

        if User.objects(email=email).first():
            raise ValueError("Email already exists")

        role = payload.get("role", User.ROLE_CUSTOMER)
        key = payload.get("key")

        if role == User.ROLE_STAFF and key != settings.SECRET_KEY_FOR_STAFF_USER:
            raise ValueError("Invalid staff key")

        if role == User.ROLE_ADMIN and key != settings.SECRET_KEY_FOR_ADMIN_USER:
            raise ValueError("Invalid admin key")

        image_url = ""

        if image_file:
            image_url = S3Service().upload_image(image_file, folder=settings.S3_USERS_FOLDER)

        user = User(
            name=payload["name"],
            email=email,
            phone=payload["phone"],
            image=image_url,
            role=role,
        )

        user.set_password(payload["password"])
        user.save()

        return user

    @staticmethod
    def update_profile(user, payload, image_file=None):

        if "name" in payload:
            user.name = payload["name"]

        if "email" in payload:
            new_email = (payload["email"] or "").strip().lower()
            if new_email and new_email != user.email:
                if User.objects(email=new_email).first():
                    raise ValueError("Email already in use")
                user.email = new_email

        if "phone" in payload:
            user.phone = payload["phone"]

        if "old_password" in payload and "new_password" in payload:
            if not user.check_password(payload["old_password"]):
                raise ValueError("Current password is incorrect")
            user.set_password(payload["new_password"])

        if image_file:

            # delete old image if exists
            if user.image:
                try:
                    S3Service().delete_image(user.image)
                except Exception:
                    pass

            user.image = S3Service().upload_image(image_file, folder=settings.S3_USERS_FOLDER)

        user.save()

        return user

    @staticmethod
    def delete_user(request_user, target_user):
        if request_user.role == User.ROLE_ADMIN:
            pass

        elif str(request_user.id) == str(target_user.id):
            pass

        else:
            raise ValueError("You can only delete your own account")

        if target_user.image:
            try:
                S3Service().delete_image(target_user.image)
            except Exception:
                pass

        target_user.delete()