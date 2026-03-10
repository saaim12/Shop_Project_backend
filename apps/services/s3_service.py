import boto3
from uuid import uuid4
from django.conf import settings


class UploadValidationError(Exception):
    pass


class UploadFailedError(Exception):
    pass


class S3Service:

    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=settings.DO_SPACES_REGION,
            endpoint_url=settings.DO_SPACES_ENDPOINT,
            aws_access_key_id=settings.DO_SPACES_KEY,
            aws_secret_access_key=settings.DO_SPACES_SECRET,
        )

    def upload_image(self, file, folder="users"):

        if not file:
            raise UploadValidationError("Image file is required")

        filename = f"{folder}/{uuid4()}_{file.name}"

        try:
            file.seek(0)

            self.client.upload_fileobj(
                file,
                settings.DO_SPACES_BUCKET,
                filename,
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": getattr(file, "content_type", "image/jpeg"),
                },
            )

        except Exception as e:
            print("S3 UPLOAD ERROR:", e)
            raise UploadFailedError("Image upload failed")

        return f"{settings.DO_SPACES_BASE_URL.rstrip('/')}/{filename}"

    def delete_image(self, file_url):

        if not file_url:
            return

        prefix = settings.DO_SPACES_BASE_URL.rstrip("/") + "/"

        if not file_url.startswith(prefix):
            return

        key = file_url[len(prefix):]

        if not key:
            return

        try:
            self.client.delete_object(
                Bucket=settings.DO_SPACES_BUCKET,
                Key=key
            )
        except Exception as e:
            print("S3 DELETE ERROR:", e)