import os
from django.core.files.base import ContentFile

def generate_unique_filename(filename):
    """Generate unique filename with timestamp."""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    return timestamp + filename

def format_response(data, message='Success', status='success'):
    """Format API response."""
    return {
        'status': status,
        'message': message,
        'data': data
    }

def format_error_response(message, errors=None, status_code=400):
    """Format error response."""
    return {
        'status': 'error',
        'message': message,
        'errors': errors,
        'status_code': status_code
    }

def serialize_queryset(queryset, serializer_class):
    """Serialize a queryset using the provided serializer."""
    serializer = serializer_class(queryset, many=True)
    return serializer.data
