from django.core.management.base import BaseCommand

from apps.cars.models import Car
from apps.inventory.models import Inventory
from apps.rims.models import Rim
from apps.spare_parts.models import SparePart
from apps.tyres.models import Tyre
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed mock data for spare parts, cars, tyres, rims and inventory"

    def handle(self, *args, **options):
        admin = User.objects(email="admin@garage.local").first()
        if not admin:
            admin = User(
                name="System Admin",
                email="admin@garage.local",
                age=35,
                phone_number="+10000000001",
                role=User.ROLE_ADMIN,
            )
            admin.set_password("Admin@1234")
            admin.save()

        spare_parts = [
            {
                "name": "Brake Pad Set",
                "brand": "Brembo",
                "model": "Universal",
                "model_year": 2020,
                "vehicle_type": SparePart.VEHICLE_CAR,
                "category": "Brake system",
                "condition": "NEW",
                "description": "Front axle pads",
                "item_number": "BP-001",
                "engine_code": "",
                "oem_numbers": "OEM-BP-001",
            },
            {
                "name": "Oil Filter",
                "brand": "Bosch",
                "model": "Corolla",
                "model_year": 2019,
                "vehicle_type": SparePart.VEHICLE_CAR,
                "category": "Filters",
                "condition": "NEW",
                "description": "Engine oil filter",
                "item_number": "OF-002",
                "engine_code": "2ZR",
                "oem_numbers": "OEM-OF-002",
            },
            {
                "name": "Alternator",
                "brand": "Denso",
                "model": "Civic",
                "model_year": 2020,
                "vehicle_type": SparePart.VEHICLE_CAR,
                "category": "Engine parts",
                "condition": "REFURBISHED",
                "description": "Refurbished alternator",
                "item_number": "ALT-003",
                "engine_code": "R18",
                "oem_numbers": "OEM-ALT-003",
            },
        ]

        cars = [
            {
                "name": "Corolla",
                "brand": "Toyota",
                "model": "LE",
                "model_year": 2019,
                "year": 2019,
                "condition": "USED",
                "chassis_number": "JTDBR32E120123451",
                "description": "Daily driver",
            },
            {
                "name": "Civic",
                "brand": "Honda",
                "model": "EX",
                "model_year": 2020,
                "year": 2020,
                "condition": "USED",
                "chassis_number": "2HGFC2F69LH123452",
                "description": "Compact sedan",
            },
            {
                "name": "Model 3",
                "brand": "Tesla",
                "model": "Long Range",
                "model_year": 2022,
                "year": 2022,
                "condition": "NEW",
                "chassis_number": "5YJ3E1EA8MF123453",
                "description": "Electric vehicle",
            },
        ]

        tyres = [
            {"company": "Michelin", "condition": "NEW", "inches": 17, "type": "All Season", "description": "Road tyre"},
            {"company": "Bridgestone", "condition": "USED", "inches": 18, "type": "Performance", "description": "Sport tyre"},
            {"company": "Pirelli", "condition": "REFURBISHED", "inches": 16, "type": "Winter", "description": "Winter tyre"},
        ]

        rims = [
            {"company": "Enkei", "condition": "NEW", "inches": 17, "type": "Alloy", "description": "Lightweight alloy"},
            {"company": "BBS", "condition": "USED", "inches": 18, "type": "Forged", "description": "Forged rim"},
            {"company": "OZ", "condition": "REFURBISHED", "inches": 16, "type": "Cast", "description": "Refurbished cast rim"},
        ]

        spare_part_docs = []
        for item in spare_parts:
            doc = SparePart.objects(name=item["name"], brand=item["brand"]).first()
            if not doc:
                doc = SparePart(**item)
                doc.save()
            spare_part_docs.append(doc)

        car_docs = []
        for item in cars:
            doc = Car.objects(chassis_number=item["chassis_number"]).first()
            if not doc:
                doc = Car(**item)
                doc.save()
            car_docs.append(doc)

        tyre_docs = []
        for item in tyres:
            doc = Tyre.objects(company=item["company"], inches=item["inches"], type=item["type"]).first()
            if not doc:
                doc = Tyre(**item)
                doc.save()
            tyre_docs.append(doc)

        rim_docs = []
        for item in rims:
            doc = Rim.objects(company=item["company"], inches=item["inches"], type=item["type"]).first()
            if not doc:
                doc = Rim(**item)
                doc.save()
            rim_docs.append(doc)

        inventory_seeds = [
            (spare_part_docs[0], 10, "A-R1-S1"),
            (spare_part_docs[1], 6, "A-R1-S2"),
            (spare_part_docs[2], 4, "A-R2-S1"),
        ]

        for spare_part, quantity, position in inventory_seeds:
            inventory = Inventory.objects(spare_part=spare_part).first()
            if not inventory:
                inventory = Inventory(
                    spare_part=spare_part,
                    quantity=quantity,
                    storage_position=position,
                    added_by=admin,
                )
                inventory.save()

        self.stdout.write(self.style.SUCCESS("Mock data seeded successfully."))
