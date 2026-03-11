import os
import sys
from typing import Any, Dict, Optional
from unittest.mock import patch

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from rest_framework.test import APIClient

from apps.cars.models import Car
from apps.inventory.models import Inventory
from apps.orders.models import Order
from apps.spare_parts.models import SparePart
from apps.users.models import User


class APITestRunner:
    def __init__(self):
        self.client = APIClient()
        self.total = 0
        self.passed = 0
        self.failed = 0

        self.tokens: Dict[str, str] = {}
        self.ids: Dict[str, str] = {}

    def log(self, message: str) -> None:
        print(message)

    def ok(self, message: str) -> None:
        self.passed += 1
        self.log(f"PASS: {message}")

    def fail(self, message: str) -> None:
        self.failed += 1
        self.log(f"FAIL: {message}")

    def request(
        self,
        method: str,
        path: str,
        expected_status: int,
        *,
        token: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        format: str = "json",
        label: Optional[str] = None,
    ):
        self.total += 1

        if token:
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        else:
            self.client.credentials()

        response = getattr(self.client, method)(path, data=data or {}, format=format)

        name = label or f"{method.upper()} {path}"
        if response.status_code == expected_status:
            self.ok(name)
        else:
            self.fail(f"{name} expected {expected_status}, got {response.status_code}, body={getattr(response, 'data', response.content)}")

        return response

    def cleanup_db(self) -> None:
        Order.drop_collection()
        Inventory.drop_collection()
        SparePart.drop_collection()
        Car.drop_collection()
        User.drop_collection()

    def run(self) -> int:
        self.log("Starting full API smoke test...")
        self.cleanup_db()

        with patch("apps.services.s3_service.S3Service.upload_image", side_effect=self._mock_upload), patch(
            "apps.services.s3_service.S3Service.delete_image", return_value=None
        ):
            self._run_auth_and_users()
            self._run_cars()
            self._run_spare_parts()
            self._run_inventory()
            self._run_orders()

        self.log("\nTest Summary")
        self.log(f"Total: {self.total}")
        self.log(f"Passed: {self.passed}")
        self.log(f"Failed: {self.failed}")

        self.cleanup_db()
        return 0 if self.failed == 0 else 1

    @staticmethod
    def _mock_upload(file_obj, folder="users"):
        name = getattr(file_obj, "name", "image.jpg")
        return f"https://mock-space.local/{folder}/{name}"

    def _run_auth_and_users(self) -> None:
        # Register users
        admin_register = self.request(
            "post",
            "/api/auth/register/",
            201,
            data={
                "name": "Admin One",
                "email": "admin@example.com",
                "password": "Pass1234",
                "phone": "+923001111111",
                "role": "admin",
                "key": settings.SECRET_KEY_FOR_ADMIN_USER,
            },
            label="Register admin",
        )
        self.ids["admin_id"] = admin_register.data["data"]["id"]

        staff_register = self.request(
            "post",
            "/api/auth/register/",
            201,
            data={
                "name": "Staff One",
                "email": "staff@example.com",
                "password": "Pass1234",
                "phone": "+923001111112",
                "role": "staff",
                "key": settings.SECRET_KEY_FOR_STAFF_USER,
            },
            label="Register staff",
        )
        self.ids["staff_id"] = staff_register.data["data"]["id"]

        customer_register = self.request(
            "post",
            "/api/auth/register/",
            201,
            data={
                "name": "Customer One",
                "email": "customer@example.com",
                "password": "Pass1234",
                "phone": "+923001111113",
                "role": "customer",
            },
            label="Register customer",
        )
        self.ids["customer_id"] = customer_register.data["data"]["id"]

        # Login users
        for role, email in (("admin", "admin@example.com"), ("staff", "staff@example.com"), ("customer", "customer@example.com")):
            login = self.request(
                "post",
                "/api/auth/login/",
                200,
                data={"email": email, "password": "Pass1234"},
                label=f"Login {role}",
            )
            self.tokens[role] = login.data["data"]["access"]
            if role == "admin":
                self.tokens["admin_refresh"] = login.data["data"]["refresh"]

        # Refresh token
        self.request(
            "post",
            "/api/auth/refresh/",
            200,
            data={"refresh": self.tokens["admin_refresh"]},
            label="Refresh token",
        )

        # Profile endpoints
        self.request("get", "/api/users/profile/", 200, token=self.tokens["customer"], label="Get profile")
        self.request(
            "put",
            "/api/users/profile/",
            200,
            token=self.tokens["customer"],
            data={"name": "Customer Updated", "phone": "+923001111999"},
            label="Update profile",
        )
        self.request("get", "/api/users/me/", 200, token=self.tokens["customer"], label="Get me")

        # Users list filters
        self.request("get", "/api/users/getall?role=all", 200, token=self.tokens["admin"], label="List users role=all")
        self.request("get", "/api/users/getall?role=staff", 200, token=self.tokens["admin"], label="List users role=staff")
        self.request(
            "get",
            "/api/users/getall?group_by_role=true",
            200,
            token=self.tokens["admin"],
            label="List users grouped",
        )

        # User detail get and update
        self.request(
            "get",
            f"/api/users/{self.ids['staff_id']}/",
            200,
            token=self.tokens["admin"],
            label="Get user by id",
        )
        self.request(
            "patch",
            f"/api/users/{self.ids['staff_id']}/",
            200,
            token=self.tokens["admin"],
            data={"phone": "+923001555555"},
            label="Patch user by id",
        )

    def _run_cars(self) -> None:
        self.request("get", "/api/cars/get-all/", 200, label="Public list cars")

        car_create = self.request(
            "post",
            "/api/cars/create/",
            201,
            token=self.tokens["staff"],
            data={
                "number_plate": "ABC123",
                "color": "Red",
                "brand": "Toyota",
                "model": "Corolla",
                "year": 2018,
            },
            label="Create car",
        )
        self.ids["car_id"] = car_create.data["data"]["id"]

        self.request("get", f"/api/cars/{self.ids['car_id']}/", 200, label="Public get car by id")

        self.request(
            "patch",
            f"/api/cars/{self.ids['car_id']}/",
            200,
            token=self.tokens["admin"],
            data={"color": "Black"},
            label="Patch car",
        )

        # Car images add/delete
        from django.core.files.uploadedfile import SimpleUploadedFile

        img1 = SimpleUploadedFile("car1.jpg", b"fakeimg1", content_type="image/jpeg")
        img2 = SimpleUploadedFile("car2.jpg", b"fakeimg2", content_type="image/jpeg")

        add_images = self.request(
            "post",
            f"/api/cars/{self.ids['car_id']}/images/",
            200,
            token=self.tokens["staff"],
            data={"images": [img1, img2]},
            format="multipart",
            label="Add car images",
        )

        image_url = add_images.data["data"]["images"][0]
        self.request(
            "delete",
            f"/api/cars/{self.ids['car_id']}/images/",
            200,
            token=self.tokens["staff"],
            data={"image_url": image_url},
            label="Delete one car image",
        )
        self.request(
            "delete",
            f"/api/cars/{self.ids['car_id']}/images/",
            200,
            token=self.tokens["staff"],
            data={"delete_all": True},
            label="Delete all car images",
        )

    def _run_spare_parts(self) -> None:
        self.request("get", "/api/spare-parts/", 200, label="Public list spare parts")

        self.request(
            "get",
            "/api/spare-parts/create-data/",
            200,
            token=self.tokens["staff"],
            label="Get spare part create-data",
        )

        spare_create = self.request(
            "post",
            "/api/spare-parts/",
            201,
            token=self.tokens["staff"],
            data={
                "name": "Brake Disc",
                "description": "A brake disc",
                "category": "brakes",
                "price": 120.5,
                "quantity": 3,
                "condition": "used",
                "car_id": self.ids["car_id"],
            },
            label="Create spare part",
        )
        if spare_create.status_code == 201 and spare_create.data["data"].get("category") != "brakes":
            self.fail("Create spare part returned unexpected category")
        self.ids["part_id"] = spare_create.data["data"]["id"]

        self.request(
            "get",
            "/api/spare-parts/?condition=used&page=1&page_size=10",
            200,
            label="Filter spare parts by condition",
        )
        self.request("get", f"/api/spare-parts/{self.ids['part_id']}/", 200, label="Public get spare part by id")

        self.request(
            "patch",
            f"/api/spare-parts/{self.ids['part_id']}/",
            200,
            token=self.tokens["admin"],
            data={"quantity": 5, "car_id": self.ids["car_id"]},
            label="Patch spare part",
        )

        from django.core.files.uploadedfile import SimpleUploadedFile

        img1 = SimpleUploadedFile("part1.jpg", b"fakeimg1", content_type="image/jpeg")
        img2 = SimpleUploadedFile("part2.jpg", b"fakeimg2", content_type="image/jpeg")

        add_images = self.request(
            "post",
            f"/api/spare-parts/{self.ids['part_id']}/images/",
            200,
            token=self.tokens["staff"],
            data={"images": [img1, img2]},
            format="multipart",
            label="Add spare part images",
        )
        spare_image = add_images.data["data"]["images"][0]

        self.request(
            "delete",
            f"/api/spare-parts/{self.ids['part_id']}/images/",
            200,
            token=self.tokens["staff"],
            data={"image_url": spare_image},
            label="Delete one spare part image",
        )
        self.request(
            "delete",
            f"/api/spare-parts/{self.ids['part_id']}/images/",
            200,
            token=self.tokens["staff"],
            data={"delete_all": True},
            label="Delete all spare part images",
        )

    def _run_inventory(self) -> None:
        # Create inventory row directly because there is no create inventory API.
        staff = User.objects(id=self.ids["staff_id"]).first()
        part = SparePart.objects(id=self.ids["part_id"]).first()
        inv = Inventory(spare_part=part, quantity=8, updated_by=staff)
        inv.save()
        self.ids["inventory_id"] = str(inv.id)

        self.request("get", "/api/inventory/", 200, token=self.tokens["staff"], label="List inventory")
        self.request(
            "patch",
            f"/api/inventory/{self.ids['inventory_id']}/",
            200,
            token=self.tokens["staff"],
            data={"quantity": 10},
            label="Patch inventory quantity",
        )

    def _run_orders(self) -> None:
        create_order = self.request(
            "post",
            "/api/orders/",
            201,
            token=self.tokens["customer"],
            data={"spare_part_ids": [self.ids["part_id"]]},
            label="Create order",
        )
        self.ids["order_id"] = create_order.data["data"]["id"]

        self.request("get", "/api/orders/", 200, token=self.tokens["customer"], label="List orders (customer)")
        self.request("get", "/api/orders/", 200, token=self.tokens["staff"], label="List orders (staff)")
        self.request(
            "get",
            f"/api/orders/{self.ids['order_id']}/",
            200,
            token=self.tokens["customer"],
            label="Get order by id",
        )
        self.request(
            "patch",
            f"/api/orders/{self.ids['order_id']}/",
            200,
            token=self.tokens["staff"],
            data={"status": "confirmed"},
            label="Patch order status",
        )

        # cover delete user alias endpoint and logout at end
        self.request(
            "delete",
            f"/api/users/deleting/{self.ids['customer_id']}/",
            200,
            token=self.tokens["admin"],
            label="Delete user via legacy deleting endpoint",
        )
        self.request("post", "/api/auth/logout/", 200, token=self.tokens["staff"], label="Logout")


def main() -> int:
    runner = APITestRunner()
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
