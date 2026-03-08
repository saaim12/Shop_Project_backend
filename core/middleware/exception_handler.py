import logging
import json
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class ExceptionHandlerMiddleware:
    """
    Global exception handler middleware.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return JsonResponse(
                {
                    'error': 'Internal server error',
                    'message': str(e) if settings.DEBUG else 'An error occurred'
                },
                status=500
            )

class RequestLoggingMiddleware:
    """
    Middleware to log all requests.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"{request.method} {request.path} - User: {request.user}")
        response = self.get_response(request)
        return response
