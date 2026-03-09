from apps.users.models import User
from apps.services.s3_service import S3Service


class UserService:
    @staticmethod
    def create_user(data, image_file=None):
        if image_file:
            s3_service = S3Service()
            image_url = s3_service.upload_image(image_file)
            data["image"] = image_url

        password = data.pop("password")
        user = User.objects.create_user(password=password, **data)
        return user

    @staticmethod
    def create_superuser(data, key, image_file=None):
        if image_file:
            s3_service = S3Service()
            image_url = s3_service.upload_image(image_file)
            data["image"] = image_url

        password = data.pop("password")
        user = User.objects.create_superuser(password=password, key=key, **data)
        return user

    @staticmethod
    def get_user_info(user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def delete_user(user_id):
        user = User.objects.filter(id=user_id).first()

        if not user:
            raise ValueError("User not found")

        if user.image:
            s3_service = S3Service()
            s3_service.delete_image(user.image)

        user.delete()
        return True

    @staticmethod
    def list_users(filters=None):
        filters = filters or {}
        queryset = User.objects.all().order_by("-created_at")

        email = (filters.get("email") or "").strip()
        user_type = (filters.get("user_type") or "").strip()
        is_active = filters.get("is_active")

        if email:
            queryset = queryset.filter(email__icontains=email)
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        return queryset

    @staticmethod
    def update_user_profile(user_id, data, image_file=None):
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise ValueError("User not found")

        old_image = user.image

        for field in ["first_name", "last_name", "phone", "age"]:
            if field in data:
                setattr(user, field, data[field])

        if image_file:
            s3_service = S3Service()
            image_url = s3_service.upload_image(image_file)
            user.image = image_url
            if old_image:
                s3_service.delete_image(old_image)

        user.full_clean()
        user.save()
        return user

    @staticmethod
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValueError("Old password is incorrect")

        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])
        return True

    @staticmethod
    def soft_delete_user(user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise ValueError("User not found")

        user.is_active = False
        user.save(update_fields=["is_active", "updated_at"])
        return True
