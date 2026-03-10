import logging


logger = logging.getLogger("app")


class APIErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code >= 400:
            user_id = None
            user = getattr(request, "user", None)
            if user and getattr(user, "is_authenticated", False):
                user_id = str(getattr(user, "id", ""))

            error_message = "HTTP error"
            if hasattr(response, "data") and isinstance(response.data, dict):
                error_message = str(response.data.get("error", response.data))

            logger.error(
                "api_error endpoint=%s method=%s user_id=%s status=%s error=%s",
                request.path,
                request.method,
                user_id or "anonymous",
                response.status_code,
                error_message,
            )

        return response
