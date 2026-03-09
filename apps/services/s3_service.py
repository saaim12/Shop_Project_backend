import boto3
from django.conf import settings
from uuid import uuid4


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
        """
        Uploads file to DigitalOcean Space
        and returns the public URL
        """

        filename = f"{folder}/{uuid4()}_{file.name}"

        self.client.upload_fileobj(
            file,
            settings.DO_SPACES_BUCKET,
            filename,
            ExtraArgs={"ACL": "public-read"}
        )

        file_url = f"{settings.DO_SPACES_BASE_URL}/{filename}"

        return file_url

    def delete_image(self, file_url):
        """
        Deletes image from s3_bucket
        """
        if not file_url or not settings.DO_SPACES_BASE_URL:
            return

        prefix = settings.DO_SPACES_BASE_URL.rstrip("/") + "/"
        if not file_url.startswith(prefix):
            return

        key = file_url[len(prefix):]
        if not key:
            return

        self.client.delete_object(
            Bucket=settings.DO_SPACES_BUCKET,
            Key=key
        )