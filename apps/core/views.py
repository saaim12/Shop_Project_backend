from django.conf import settings
from django.http import JsonResponse

from config.mongo import is_mongo_connected


def home(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "Auto Spare Parts API",
            "database": "connected" if is_mongo_connected() else "disconnected",
            "debug": settings.DEBUG,
        }
    )
