from django.conf import settings
from django.http import JsonResponse

from config.mongo import is_mongo_connected


def home(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "Garage Backend fully active",
            "database": "Mongo DB is connected" if is_mongo_connected() else "Mongo DB is not connected",
            "debug": settings.DEBUG,
        }
    )
