from rest_framework.exceptions import APIException

class CustomBadRequest(APIException):
    status_code = 400
    default_detail = 'Bad request'
    default_code = 'bad_request'

class CustomNotFound(APIException):
    status_code = 404
    default_detail = 'Resource not found'
    default_code = 'not_found'

class CustomServerError(APIException):
    status_code = 500
    default_detail = 'Internal server error'
    default_code = 'server_error'

class ValidationException(APIException):
    status_code = 422
    default_detail = 'Validation error'
    default_code = 'validation_error'
