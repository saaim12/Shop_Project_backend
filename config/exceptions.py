import logging

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import exception_handler


logger = logging.getLogger("app")


def custom_exception_handler(exc, context):
    request = context.get("request")
    response = exception_handler(exc, context)

    if response is None:
        logger.exception(
            "unhandled_exception endpoint=%s method=%s user_id=%s error=%s",
            getattr(request, "path", "unknown"),
            getattr(request, "method", "unknown"),
            str(getattr(getattr(request, "user", None), "id", "anonymous")),
            str(exc),
        )
        return JsonResponse(
            {"success": False, "error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    detail = "Request failed"
    if isinstance(response.data, dict):
        if "detail" in response.data:
            detail = str(response.data["detail"])
        else:
            detail = "Invalid request data"
    elif isinstance(response.data, list) and response.data:
        detail = str(response.data[0])

    response.data = {"success": False, "error": detail}
    return response


def custom_404(request, exception=None):
    return JsonResponse({"success": False, "error": "Endpoint not found"}, status=404)
