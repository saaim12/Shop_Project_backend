from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings

from apps.services.s3_service import S3Service


class S3ServiceTests(SimpleTestCase):
    @override_settings(
        USE_S3_STORAGE=True,
        DO_SPACES_REGION="sfo3",
        DO_SPACES_ENDPOINT="https://sfo3.digitaloceanspaces.com",
        DO_SPACES_KEY="key",
        DO_SPACES_SECRET="secret",
        DO_SPACES_BUCKET="bucket",
        DO_SPACES_BASE_URL="https://bucket.sfo3.digitaloceanspaces.com",
    )
    def test_upload_image_returns_s3_url(self):
        mock_client = Mock()

        with patch("apps.services.s3_service.boto3.client", return_value=mock_client):
            service = S3Service()
            file_obj = SimpleUploadedFile("customer one.jpeg", b"fake-image", content_type="image/jpeg")
            image_url = service.upload_image(file_obj, folder="users")

        mock_client.upload_fileobj.assert_called_once()
        self.assertTrue(image_url.startswith("https://bucket.sfo3.digitaloceanspaces.com/users/"))
        self.assertNotIn(" ", image_url)
        self.assertTrue(image_url.endswith("_customer_one.jpeg"))
