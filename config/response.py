from rest_framework.response import Response


def extract_error_message(errors, fallback="Invalid request data"):
    def _first_error(value, prefix=""):
        if isinstance(value, dict):
            for key, nested in value.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                found = _first_error(nested, path)
                if found:
                    return found
            return None

        if isinstance(value, list) and value:
            first = value[0]
            if isinstance(first, (dict, list)):
                return _first_error(first, prefix)
            return f"{prefix}: {first}" if prefix else str(first)

        if isinstance(value, str):
            return f"{prefix}: {value}" if prefix else value

        return None

    message = _first_error(errors)
    if message:
        return message
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
