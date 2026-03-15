import shutil
import tempfile
from unittest.mock import patch

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.cars.models import Car
from apps.orders.models import Order
from apps.services.s3_service import UploadFailedError
from apps.spare_parts.models import SparePart
from apps.users.models import User


PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa7\x89\x81\xf3\x00\x00\x00\x00IEND\xaeB`\x82"
)


class AutoSparePartsAPITestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._temp_media = tempfile.mkdtemp(prefix="shop_media_")
        cls._override = override_settings(USE_S3_STORAGE=False, MEDIA_ROOT=cls._temp_media, MEDIA_URL="/media/")
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        shutil.rmtree(cls._temp_media, ignore_errors=True)
        super().tearDownClass()

    def tearDown(self):
        Order.drop_collection()
        SparePart.drop_collection()
        Car.drop_collection()
        User.drop_collection()
        super().tearDown()

    def _image(self, name="img.png"):
        return SimpleUploadedFile(name=name, content=PNG_BYTES, content_type="image/png")

    def _register(self, name, email, password, phone, role="customer", key="", image=None):
        payload = {
            "name": name,
            "email": email,
            "password": password,
            "phone": phone,
            "role": role,
        }
        if key:
            payload["key"] = key
        if image is not None:
            payload["image"] = image
            return self.client.post("/api/auth/register/", payload, format="multipart")
        return self.client.post("/api/auth/register/", payload, format="json")

    def _login(self, email, password):
        response = self.client.post("/api/auth/login/", {"email": email, "password": password}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["data"]["access"]

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_user_image_upload_and_retrieval(self):
        register = self._register(
            "User Img",
            "userimg@example.com",
            "Pass1234",
            "+923001111111",
            image=self._image("avatar.png"),
        )
        self.assertEqual(register.status_code, status.HTTP_201_CREATED)
        self.assertTrue(register.data["data"]["image"].startswith("/media/users/"))

        token = self._login("userimg@example.com", "Pass1234")
        self._auth(token)
        profile = self.client.get("/api/users/profile/")
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertTrue(profile.data["data"]["image"].startswith("/media/users/"))

    def test_car_and_spare_part_multiple_image_uploads(self):
        self._register(
            "Staff One",
            "staff@example.com",
            "Pass1234",
            "+923002222222",
            role="staff",
            key=settings.SECRET_KEY_FOR_STAFF_USER,
        )

        staff_token = self._login("staff@example.com", "Pass1234")
        self._auth(staff_token)

        car_resp = self.client.post(
            "/api/cars/create/",
            {
                "number_plate": "ABC-1234",
                "color": "Blue",
                "brand": "BMW",
                "model": "M3",
                "year": 2020,
                "model_year": 2015,
                "kilometer": 130000,
                "first_registration": "01/2015",
                "description": "Export car, Inquiry number: A2500465",
                "images": [self._image("car1.png"), self._image("car2.png")],
            },
            format="multipart",
        )
        self.assertEqual(car_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(car_resp.data["data"]["images"]), 2)
        self.assertTrue(all(url.startswith("/media/cars/") for url in car_resp.data["data"]["images"]))
        self.assertEqual(car_resp.data["data"]["model_year"], 2015)
        self.assertEqual(car_resp.data["data"]["kilometer"], 130000)
        self.assertEqual(car_resp.data["data"]["first_registration"], "01/2015")
        self.assertEqual(car_resp.data["data"]["description"], "Export car, Inquiry number: A2500465")
        car_id = car_resp.data["data"]["id"]

        part_resp = self.client.post(
            "/api/spare-parts/",
            {
                "name": "Brake Disc",
                "description": "Used",
                "category": "brakes",
                "price": 150,
                "condition": "used",
                "car_id": car_id,
                "images": [self._image("sp1.png"), self._image("sp2.png")],
            },
            format="multipart",
        )
        self.assertEqual(part_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(part_resp.data["data"]["images"]), 2)
        self.assertTrue(all(url.startswith("/media/spare_parts/") for url in part_resp.data["data"]["images"]))
        self.assertEqual(part_resp.data["data"]["category"], "brakes")
        self.assertEqual(part_resp.data["data"]["car_id"], car_id)

        cars_get = self.client.get(f"/api/cars/{car_id}/")
        self.assertEqual(cars_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(cars_get.data["data"]["images"]), 2)

        part_id = part_resp.data["data"]["id"]
        spare_get = self.client.get(f"/api/spare-parts/{part_id}/")
        self.assertEqual(spare_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(spare_get.data["data"]["images"]), 2)

    def test_invalid_image_format_rejected(self):
        bad_file = SimpleUploadedFile("not-image.txt", b"hello", content_type="text/plain")
        response = self._register(
            "Bad Image",
            "badimage@example.com",
            "Pass1234",
            "+923003333333",
            image=bad_file,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid image format")

    def test_invalid_email_registration(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "name": "Bad Email",
                "email": "invalid-email",
                "password": "Pass1234",
                "phone": "+923003333333",
                "role": "customer",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Email address is not valid")

    def test_missing_required_fields_registration(self):
        response = self.client.post(
            "/api/auth/register/",
            {"name": "No Password", "email": "nopass@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data["error"], {"This field is required.", "Invalid request data"})

    def test_invalid_permission_customer_create_car(self):
        self._register("Cust", "cust@example.com", "Pass1234", "+923009999999")
        token = self._login("cust@example.com", "Pass1234")
        self._auth(token)

        response = self.client.post(
            "/api/cars/create/",
            {
                "number_plate": "CUST-1111",
                "color": "Black",
                "brand": "Honda",
                "model": "Civic",
                "year": 2022,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "Only staff or admin can create cars")

    def test_invalid_used_spare_part_car_reference(self):
        self._register(
            "Staff One",
            "staff-invalid-car@example.com",
            "Pass1234",
            "+923001010101",
            role="staff",
            key=settings.SECRET_KEY_FOR_STAFF_USER,
        )
        staff_token = self._login("staff-invalid-car@example.com", "Pass1234")
        self._auth(staff_token)

        response = self.client.post(
            "/api/spare-parts/",
            {
                "name": "Brake Disc",
                "description": "Used",
                "category": "brakes",
                "price": 200,
                "condition": "used",
                "car_id": "507f1f77bcf86cd799439011",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid car reference")

    def test_upload_failure_does_not_create_document(self):
        with patch("apps.services.s3_service.S3Service.upload_image", side_effect=UploadFailedError("Image upload failed")):
            response = self._register(
                "Fail User",
                "failupload@example.com",
                "Pass1234",
                "+923004444444",
                image=self._image("fail.png"),
            )
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIsNone(User.objects(email="failupload@example.com").first())

    def test_invalid_permission_customer_cannot_create_or_delete_spare_part(self):
        self._register("Cust", "cust-sp@example.com", "Pass1234", "+923008888888")
        token = self._login("cust-sp@example.com", "Pass1234")
        self._auth(token)

        create_response = self.client.post(
            "/api/spare-parts/",
            {
                "name": "Air Filter",
                "description": "Customer should not create",
                "category": "filter",
                "price": 40,
                "condition": "new",
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(create_response.data["error"], "Only staff or admin can create spare parts")

        staff_register = self._register(
            "Staff Two",
            "staff2@example.com",
            "Pass1234",
            "+923007777777",
            role="staff",
            key=settings.SECRET_KEY_FOR_STAFF_USER,
        )
        self.assertEqual(staff_register.status_code, status.HTTP_201_CREATED)
        staff_token = self._login("staff2@example.com", "Pass1234")
        self._auth(staff_token)

        create_by_staff = self.client.post(
            "/api/spare-parts/",
            {
                "name": "Headlight Bulb",
                "description": "Created by staff",
                "category": "headlights",
                "price": 55,
                "condition": "new",
            },
            format="json",
        )
        self.assertEqual(create_by_staff.status_code, status.HTTP_201_CREATED)
        part_id = create_by_staff.data["data"]["id"]

        self._auth(token)
        delete_response = self.client.delete(f"/api/spare-parts/{part_id}/")
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.data["error"], "Only staff or admin can delete spare parts")

    def test_delete_spare_part_removes_images_from_storage(self):
        self._register(
            "Staff Img",
            "staffimg@example.com",
            "Pass1234",
            "+923006666666",
            role="staff",
            key=settings.SECRET_KEY_FOR_STAFF_USER,
        )
        staff_token = self._login("staffimg@example.com", "Pass1234")
        self._auth(staff_token)

        part_resp = self.client.post(
            "/api/spare-parts/",
            {
                "name": "Filter Set",
                "description": "Delete cleanup",
                "category": "filter",
                "price": 25,
                "condition": "new",
                "images": [self._image("a.png"), self._image("b.png")],
            },
            format="multipart",
        )
        self.assertEqual(part_resp.status_code, status.HTTP_201_CREATED)
        part_id = part_resp.data["data"]["id"]

        with patch("apps.services.s3_service.S3Service.delete_image") as delete_mock:
            delete_resp = self.client.delete(f"/api/spare-parts/{part_id}/")

        self.assertEqual(delete_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_mock.call_count, 2)

    def test_patch_spare_part_can_add_images(self):
        self._register(
            "Staff Patch",
            "staffpatch@example.com",
            "Pass1234",
            "+923005555555",
            role="staff",
            key=settings.SECRET_KEY_FOR_STAFF_USER,
        )
        staff_token = self._login("staffpatch@example.com", "Pass1234")
        self._auth(staff_token)

        create_resp = self.client.post(
            "/api/spare-parts/",
            {
                "name": "Patchable Part",
                "description": "No images initially",
                "category": "filter",
                "price": 75,
                "condition": "new",
            },
            format="json",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        part_id = create_resp.data["data"]["id"]
        self.assertEqual(create_resp.data["data"]["images"], [])

        patch_resp = self.client.patch(
            f"/api/spare-parts/{part_id}/",
            {"images": [self._image("p1.png"), self._image("p2.png")]},
            format="multipart",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(patch_resp.data["data"]["images"]), 2)
        self.assertTrue(all(url.startswith("/media/spare_parts/") for url in patch_resp.data["data"]["images"]))

    def test_order_customer_only_create_and_stock_deduction(self):
        self._register(
            "Staff Order",
            "staff-order@example.com",
            "Pass1234",
            "+923001234561",
            role="staff",
            key=settings.SECRET_KEY_FOR_STAFF_USER,
        )
        self._register("Customer Order", "cust-order@example.com", "Pass1234", "+923001234562")

        staff_token = self._login("staff-order@example.com", "Pass1234")
        self._auth(staff_token)
        part_resp = self.client.post(
            "/api/spare-parts/",
            {
                "name": "Orderable Brake Pad",
                "description": "Stock test",
                "category": "brakes",
                "price": 50,
                "quantity": 10,
                "condition": "new",
            },
            format="json",
        )
        self.assertEqual(part_resp.status_code, status.HTTP_201_CREATED)
        part_id = part_resp.data["data"]["id"]

        staff_order_resp = self.client.post(
            "/api/orders/",
            {"spare_part_id": part_id, "quantity": 2},
            format="json",
        )
        self.assertEqual(staff_order_resp.status_code, status.HTTP_403_FORBIDDEN)

        customer_token = self._login("cust-order@example.com", "Pass1234")
        self._auth(customer_token)
        order_resp = self.client.post(
            "/api/orders/",
            {"spare_part_id": part_id, "quantity": 2},
            format="json",
        )
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order_resp.data["data"]["quantity"], 2)
        self.assertEqual(order_resp.data["data"]["total_price"], 100.0)

        updated_part = SparePart.objects(id=part_id).first()
        self.assertEqual(updated_part.quantity, 8)

    def test_order_customer_delete_and_staff_status_update(self):
        self._register(
            "Staff Manage",
            "staff-manage@example.com",
            "Pass1234",
            "+923001234563",
            role="staff",
            key=settings.SECRET_KEY_FOR_STAFF_USER,
        )
        self._register("Customer Manage", "cust-manage@example.com", "Pass1234", "+923001234564")

        staff_token = self._login("staff-manage@example.com", "Pass1234")
        self._auth(staff_token)
        part_resp = self.client.post(
            "/api/spare-parts/",
            {
                "name": "Orderable Filter",
                "description": "Delete restore stock",
                "category": "filter",
                "price": 20,
                "quantity": 5,
                "condition": "new",
            },
            format="json",
        )
        self.assertEqual(part_resp.status_code, status.HTTP_201_CREATED)
        part_id = part_resp.data["data"]["id"]

        customer_token = self._login("cust-manage@example.com", "Pass1234")
        self._auth(customer_token)
        order_resp = self.client.post(
            "/api/orders/",
            {"spare_part_id": part_id, "quantity": 3},
            format="json",
        )
        self.assertEqual(order_resp.status_code, status.HTTP_201_CREATED)
        order_id = order_resp.data["data"]["id"]

        self._auth(staff_token)
        patch_resp = self.client.patch(
            f"/api/orders/{order_id}/",
            {"status": "confirmed"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_resp.data["data"]["status"], "confirmed")

        staff_delete = self.client.delete(f"/api/orders/{order_id}/")
        self.assertEqual(staff_delete.status_code, status.HTTP_403_FORBIDDEN)

        self._auth(customer_token)
        customer_delete = self.client.delete(f"/api/orders/{order_id}/")
        self.assertEqual(customer_delete.status_code, status.HTTP_200_OK)

        restored_part = SparePart.objects(id=part_id).first()
        self.assertEqual(restored_part.quantity, 5)
