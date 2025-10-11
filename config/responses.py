"""
Defines the custom response structure for the APIs and custom Error/API Exceptions.

ErrorCode and ERROR_MESSAGES define a fixed set of internal status labels that an API will use.
The latter stores custom messages for each internal error code.

The Pydantic schemas define the structure of the responses from the APIs and ensure consistency.
"""
from enum import Enum
from typing import Optional, Generic, TypeVar
from pydantic import Field
from ninja import Schema, NinjaAPI
from ninja.errors import HttpError, AuthenticationError
from django.http import HttpRequest


# ====================================================================
# ENUMS AND CONSTANTS
# ====================================================================

class StatusCode(int, Enum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500


class ErrorCode(str, Enum):
    SUCCESS = "SUCCESSFUL"
    INVALID_INPUT = "INVALID_INPUT"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    CONFLICT = "CONFLICT"


ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "Operation completed successfully.",
    ErrorCode.INVALID_INPUT: "The input provided is invalid.",
    ErrorCode.NOT_FOUND: "The requested resource was not found.",
    ErrorCode.UNAUTHORIZED: "You are not authorized to perform this action.",
    ErrorCode.FORBIDDEN: "You do not have permission to access this resource.",
    ErrorCode.INTERNAL_SERVER_ERROR: "An internal server error occurred.",
    ErrorCode.CONFLICT: "A conflict occurred with the current state of the resource.",
}


# ====================================================================
# GENERIC RESPONSE SCHEMAS
# ====================================================================

DataT = TypeVar("DataT")


class BaseResponseSchema(Schema, Generic[DataT]):
    """Base schema for all API responses."""
    status: str = Field(..., description="Internal API status code.")
    message: str = Field(..., description="Human-readable response message.")
    data: Optional[DataT] = None
    error: Optional[str] = None


class SuccessResponseSchema(BaseResponseSchema[DataT], Generic[DataT]):
    """Standard success response wrapper (for views)."""
    status: str = ErrorCode.SUCCESS.value
    message: str = ERROR_MESSAGES[ErrorCode.SUCCESS]
    data: DataT


class MessageResponseSchema(SuccessResponseSchema[None]):
    """Simple success response without a data payload."""
    data: None = None


class ErrorResponseSchema(BaseResponseSchema[None]):
    """Standard error response structure."""
    status: str
    message: str
    error: str
    data: None = None


# ====================================================================
# CUSTOM EXCEPTIONS
# ====================================================================

class APIException(HttpError):
    """Base custom exception for API-level business errors."""
    def __init__(
        self,
        status_code: StatusCode,
        error_code: ErrorCode,
        message: Optional[str] = None
    ):
        self.status_code = status_code.value
        self.error_code = error_code
        self.message = message or ERROR_MESSAGES.get(error_code, "Unknown API Error.")
        super().__init__(self.status_code, self.message)


class InvalidInputError(APIException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(StatusCode.BAD_REQUEST, ErrorCode.INVALID_INPUT, message)


class NotFoundError(APIException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(StatusCode.NOT_FOUND, ErrorCode.NOT_FOUND, message)


class UnauthorizedError(APIException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(StatusCode.UNAUTHORIZED, ErrorCode.UNAUTHORIZED, message)


class ForbiddenError(APIException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(StatusCode.FORBIDDEN, ErrorCode.FORBIDDEN, message)


class ConflictError(APIException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(StatusCode.CONFLICT, ErrorCode.CONFLICT, message)


class InternalServerError(APIException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(StatusCode.INTERNAL_SERVER_ERROR, ErrorCode.INTERNAL_SERVER_ERROR, message)


# ====================================================================
# EXCEPTION HANDLERS
# ====================================================================

def register_api_exception_handlers(api: NinjaAPI):
    """Registers the custom API exception handlers with the NinjaAPI instance."""

    @api.exception_handler(APIException)
    def api_exception_handler(request: HttpRequest, exc: APIException):
        error_content = {
            "status": exc.error_code.value,
            "message": exc.message,
            "error": exc.error_code.value,
            "data": None,
        }
        return api.create_response(request, error_content, status=exc.status_code)

    @api.exception_handler(AuthenticationError)
    def auth_error_handler(request: HttpRequest, exc: AuthenticationError):
        err_code = ErrorCode.UNAUTHORIZED
        error_content = {
            "status": err_code.value,
            "message": "Authentication credentials were not provided or are invalid.",
            "error": err_code.value,
            "data": str(exc),
        }
        return api.create_response(request, error_content, status=StatusCode.UNAUTHORIZED.value)

    @api.exception_handler(HttpError)
    def http_error_handler(request: HttpRequest, exc: HttpError):
        status_to_error_code = {
            StatusCode.BAD_REQUEST.value: ErrorCode.INVALID_INPUT,
            StatusCode.UNAUTHORIZED.value: ErrorCode.UNAUTHORIZED,
            StatusCode.FORBIDDEN.value: ErrorCode.FORBIDDEN,
            StatusCode.NOT_FOUND.value: ErrorCode.NOT_FOUND,
        }

        err_code = status_to_error_code.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)

        error_content = {
            "status": err_code.value,
            "message": ERROR_MESSAGES.get(err_code, "Unknown error."),
            "error": err_code.value,
            "data": None,
        }
        return api.create_response(request, error_content, status=exc.status_code)
