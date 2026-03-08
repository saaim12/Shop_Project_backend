"""Custom exception handlers for the Shop Project backend."""

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "status": "error",
            "status_code": response.status_code,
            "errors": response.data,
        }

    return response
