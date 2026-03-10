from bson import ObjectId

from apps.cars.models import Car
from apps.services.s3_service import S3Service


class CarService:
    @staticmethod
    def _check_duplicate(number_plate, brand, model, year, exclude_id=None):
        plate = (number_plate or "").strip().upper()
        brand_norm = (brand or "").strip().lower()
        model_norm = (model or "").strip().lower()

        plate_query = Car.objects(number_plate=plate)
        if exclude_id:
            plate_query = plate_query.filter(id__ne=exclude_id)
        if plate_query.first():
            raise ValueError("Number plate already exists")

        combo_query = Car.objects(
            __raw__={
                "brand": {"$regex": f"^{brand_norm}$", "$options": "i"},
                "model": {"$regex": f"^{model_norm}$", "$options": "i"},
                "year": year,
            }
        )
        if exclude_id:
            combo_query = combo_query.filter(id__ne=exclude_id)
        if combo_query.first():
            raise ValueError("A car with the same brand, model, and year already exists")

    @staticmethod
    def create_car(payload, user):
        CarService._check_duplicate(
            payload["number_plate"],
            payload["brand"],
            payload["model"],
            payload["year"],
        )

        car = Car(
            number_plate=payload["number_plate"],
            color=payload["color"],
            brand=payload["brand"],
            model=payload["model"],
            year=payload["year"],
            created_by=user,
        )
        car.save()
        return car

    @staticmethod
    def list_cars():
        return Car.objects().order_by("-created_at")

    @staticmethod
    def get_car_by_id(car_id):
        try:
            return Car.objects(id=ObjectId(car_id)).first()
        except Exception:
            return None

    @staticmethod
    def delete_car(car):
        if car.images:
            s3_service = S3Service()
            for url in list(car.images):
                try:
                    s3_service.delete_image(url)
                except Exception:
                    pass
        car.delete()

    @staticmethod
    def update_car(car, payload):
        next_number_plate = payload.get("number_plate", car.number_plate)
        next_brand = payload.get("brand", car.brand)
        next_model = payload.get("model", car.model)
        next_year = payload.get("year", car.year)

        CarService._check_duplicate(next_number_plate, next_brand, next_model, next_year, exclude_id=car.id)

        if "number_plate" in payload:
            car.number_plate = payload["number_plate"]
        if "color" in payload:
            car.color = payload["color"]
        if "brand" in payload:
            car.brand = payload["brand"]
        if "model" in payload:
            car.model = payload["model"]
        if "year" in payload:
            car.year = payload["year"]

        car.save()
        return car

    @staticmethod
    def add_images(car, image_files):
        if not image_files:
            raise ValueError("No images provided")
        s3_service = S3Service()
        for image_file in image_files:
            url = s3_service.upload_image(image_file, folder="cars")
            car.images.append(url)
        car.save()
        return car

    @staticmethod
    def delete_image(car, image_url):
        if image_url not in car.images:
            raise ValueError("Image not found on this car")
        try:
            S3Service().delete_image(image_url)
        except Exception:
            pass
        car.images.remove(image_url)
        car.save()
        return car

    @staticmethod
    def delete_all_images(car):
        s3_service = S3Service()
        for url in list(car.images):
            try:
                s3_service.delete_image(url)
            except Exception:
                pass
        car.images = []
        car.save()
        return car
