import boto3
from apps.core.settings import (DO_SPACES_KEY, DO_SPACES_SECRET, DO_SPACES_BUCKET, DO_SPACES_REGION, DO_SPACES_ENDPOINT, DO_SPACES_BASE_URL)
from uuid import uuid4


class S3Service:

    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=DO_SPACES_REGION,
            endpoint_url=DO_SPACES_ENDPOINT,
            aws_access_key_id=DO_SPACES_KEY,
            aws_secret_access_key=DO_SPACES_SECRET,
        )

    def upload_image(self, file, folder="users"):
        """
        Uploads file to DigitalOcean Space
        and returns the public URL
        """

        filename = f"{folder}/{uuid4()}_{file.name}"

        self.client.upload_fileobj(
            file,
            DO_SPACES_BUCKET,
            filename,
            ExtraArgs={"ACL": "public-read"}
        )

        file_url = f"{DO_SPACES_BASE_URL}/{filename}"

        return file_url

    def delete_image(self, file_url):
        """
        Deletes image from s3_bucket
        """

        key = file_url.split(DO_SPACES_BASE_URL + "/")[1]

        self.client.delete_object(
            Bucket=DO_SPACES_BUCKET,
            Key=key
        )