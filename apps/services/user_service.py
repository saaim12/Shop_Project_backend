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
    def delete_user(user_id):
        user = User.objects.filter(id=user_id).first()

        if not user:
            raise ValueError("User not found")

        if user.image:
            s3_service = S3Service()
            s3_service.delete_image(user.image)

        user.delete()
        return True