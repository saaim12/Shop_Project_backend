from rest_framework.response import Response


def extract_error_message(errors, fallback="Invalid request data"):
    if isinstance(errors, dict):
        for value in errors.values():
            if isinstance(value, list) and value:
                return str(value[0])
            if isinstance(value, str):
                return value
    if isinstance(errors, list) and errors:
        return str(errors[0])
    return fallback


def success_response(data=None, status_code=200, message="Request successful"):
    payload = {
        "success": True,
        "message": message,
        "data": data if data is not None else {},
    }
    return Response(payload, status=status_code)


def error_response(message, status_code=400):
    payload = {"success": False, "error": str(message)}
    return Response(payload, status=status_code)
