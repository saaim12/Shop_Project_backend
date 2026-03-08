from django.apps import AppConfig
from django.db import connections


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        try:
            conn = connections["default"]
            with conn.cursor() as cursor:
                pass
            print("MongoDB connection successful. ready to store data")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")