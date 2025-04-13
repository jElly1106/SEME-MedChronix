"""This module contains the response code for the response."""
from enum import IntEnum, unique

@unique
class ResponseCode(IntEnum):
    """The response code for the response."""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    PARAMS_ERROR = 10001
    DATA_NOT_FOUND = 10002
    DB_ERROR = 10007
