import boto3
from pathlib import Path
import re
from uuid import uuid4
from django.conf import settings
from django.core.files.storage import default_storage


class UploadValidationError(Exception):
    pass


class UploadFailedError(Exception):
    pass


class S3Service:

    @staticmethod
    def _sanitize_filename(filename):
        name = Path(filename or "upload").name
        stem = Path(name).stem
        suffix = Path(name).suffix.lower()

        cleaned_stem = re.sub(r"[^a-zA-Z0-9._-]+", "_", stem).strip("._-")
        if not cleaned_stem:
            cleaned_stem = "upload"

        return f"{cleaned_stem}{suffix}"

    def __init__(self):
        self.client = None
        if settings.USE_S3_STORAGE:
            self.client = boto3.client(
                "s3",
                region_name=settings.DO_SPACES_REGION,
                endpoint_url=settings.DO_SPACES_ENDPOINT,
                aws_access_key_id=settings.DO_SPACES_KEY,
                aws_secret_access_key=settings.DO_SPACES_SECRET,
            )

    @staticmethod
    def _validate_image_file(file):
        content_type = (getattr(file, "content_type", "") or "").lower()
        extension = Path(getattr(file, "name", "")).suffix.lower()
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

        if extension and extension not in allowed_extensions:
            raise UploadValidationError("Invalid image format")

        if content_type and not content_type.startswith("image/"):
            raise UploadValidationError("Invalid image format")

    def upload_image(self, file, folder):

        if not file:
            raise UploadValidationError("Image file is required")

        if not folder:
            raise UploadValidationError("Upload folder is required")

        self._validate_image_file(file)

        normalized_folder = str(folder).strip().strip("/")
        if not normalized_folder:
            raise UploadValidationError("Upload folder is required")

        original_name = self._sanitize_filename(getattr(file, "name", "upload"))
        filename = f"{normalized_folder}/{uuid4()}_{original_name}"

        try:
            file.seek(0)

            if not settings.USE_S3_STORAGE:
                saved_path = default_storage.save(filename, file)
                normalized_path = saved_path.replace("\\", "/")
                return f"{settings.MEDIA_URL.rstrip('/')}/{normalized_path}"

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

        if settings.USE_S3_STORAGE:
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
            return

        prefix = settings.MEDIA_URL.rstrip("/") + "/"

        if not file_url.startswith(prefix):
            return

        key = file_url[len(prefix):]

        if not key:
            return

        try:
            if default_storage.exists(key):
                default_storage.delete(key)
        except Exception as e:
            print("LOCAL DELETE ERROR:", e)