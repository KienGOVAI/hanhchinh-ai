"""
Schemas dùng chung cho toàn bộ Backend.
"""

from .api_response import ApiResponse
from .document import (
    DocumentRequest,
    DocumentResponse,
)
from .error_schema import (
    ApiError,
    ValidationErrorResponse,
    ProviderErrorResponse,
    InternalServerErrorResponse,
)

__all__ = [
    "ApiResponse",
    "DocumentRequest",
    "DocumentResponse",
    "ApiError",
    "ValidationErrorResponse",
    "ProviderErrorResponse",
    "InternalServerErrorResponse",
]