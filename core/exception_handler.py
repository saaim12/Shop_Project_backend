from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def _to_field_errors(detail):
    if isinstance(detail, dict):
        normalized = {}
        for key, value in detail.items():
            if isinstance(value, list):
                normalized[key] = [str(item) for item in value]
            else:
                normalized[key] = [str(value)]
        return normalized

    if isinstance(detail, list):
        return {"non_field_errors": [str(item) for item in detail]}

    return {"non_field_errors": [str(detail)]}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    detail = response.data.get("detail", response.data)
    payload = {
        "success": False,
        "message": "Request failed",
    }

    if isinstance(exc, ValidationError):
        payload["message"] = "Validation failed"
        payload["field_errors"] = _to_field_errors(exc.detail)
    elif "detail" in response.data:
        payload["message"] = str(response.data.get("detail"))
    elif isinstance(response.data, dict):
        field_errors = _to_field_errors(response.data)
        payload["message"] = "Validation failed"
        payload["field_errors"] = field_errors
    else:
        payload["message"] = str(detail)

    response.data = payload
    return response
