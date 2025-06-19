"""
Response models for API endpoints.
"""

from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Type variable for generic responses
T = TypeVar('T')


class ResponseStatus(str, Enum):
    """Response status enumeration."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class BaseResponse(BaseModel, Generic[T]):
    """
    Base response model for all API endpoints.
    """
    status: ResponseStatus = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": None,
                "timestamp": "2024-01-01T00:00:00Z",
                "request_id": "req_123456789"
            }
        }


class SuccessResponse(BaseResponse[T]):
    """Success response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")


class ErrorResponse(BaseResponse[None]):
    """Error response model."""
    status: ResponseStatus = Field(default=ResponseStatus.ERROR, description="Response status")
    error_code: Optional[str] = Field(None, description="Error code")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    error_type: Optional[str] = Field(None, description="Error type classification")
    stack_trace: Optional[str] = Field(None, description="Stack trace (development only)")

    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "message": "An error occurred",
                "data": None,
                "timestamp": "2024-01-01T00:00:00Z",
                "request_id": "req_123456789",
                "error_code": "VALIDATION_ERROR",
                "error_type": "client_error",
                "error_details": {
                    "field": "email",
                    "issue": "Invalid email format"
                }
            }
        }


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "per_page": 20,
                "total_pages": 5,
                "has_next": True,
                "has_prev": False
            }
        }


class PaginatedResponse(BaseResponse[List[T]]):
    """Paginated response model."""
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Data retrieved successfully",
                "data": [],
                "timestamp": "2024-01-01T00:00:00Z",
                "request_id": "req_123456789",
                "meta": {
                    "total": 100,
                    "page": 1,
                    "per_page": 20,
                    "total_pages": 5,
                    "has_next": True,
                    "has_prev": False
                }
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")
    database: Dict[str, Any] = Field(..., description="Database status")
    dependencies: Dict[str, Any] = Field(default_factory=dict, description="External dependencies status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": "2024-01-01T00:00:00Z",
                "uptime": 3600.0,
                "database": {
                    "status": "connected",
                    "projects_count": 10,
                    "sessions_count": 5,
                    "templates_count": 3
                },
                "dependencies": {
                    "gemini_api": "available",
                    "crewai": "configured"
                }
            }
        }


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""
    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Error message")
    value: Optional[Any] = Field(None, description="Invalid value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "value": "invalid-email"
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Validation error response model."""
    error_code: str = "VALIDATION_ERROR"
    validation_errors: List[ValidationErrorDetail] = Field(..., description="Validation error details")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "message": "Validation failed",
                "data": None,
                "timestamp": "2024-01-01T00:00:00Z",
                "request_id": "req_123456789",
                "error_code": "VALIDATION_ERROR",
                "validation_errors": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "value": "invalid-email"
                    }
                ]
            }
        }


class CreatedResponse(SuccessResponse[T]):
    """Response for successful creation operations."""
    message: str = "Resource created successfully"


class UpdatedResponse(SuccessResponse[T]):
    """Response for successful update operations."""
    message: str = "Resource updated successfully"


class DeletedResponse(SuccessResponse[None]):
    """Response for successful deletion operations."""
    message: str = "Resource deleted successfully"


class NotFoundResponse(ErrorResponse):
    """Response for resource not found."""
    message: str = "Resource not found"
    error_code: str = "NOT_FOUND"


class ConflictResponse(ErrorResponse):
    """Response for resource conflicts."""
    message: str = "Resource conflict"
    error_code: str = "CONFLICT"


class UnauthorizedResponse(ErrorResponse):
    """Response for unauthorized access."""
    message: str = "Unauthorized access"
    error_code: str = "UNAUTHORIZED"


class ForbiddenResponse(ErrorResponse):
    """Response for forbidden access."""
    message: str = "Access forbidden"
    error_code: str = "FORBIDDEN"


class RateLimitResponse(ErrorResponse):
    """Response for rate limit exceeded."""
    message: str = "Rate limit exceeded"
    error_code: str = "RATE_LIMIT_EXCEEDED"
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying")


class MaintenanceResponse(ErrorResponse):
    """Response for maintenance mode."""
    message: str = "Service under maintenance"
    error_code: str = "MAINTENANCE"
    estimated_completion: Optional[datetime] = Field(None, description="Estimated maintenance completion time")


class DatabaseErrorResponse(ErrorResponse):
    """Response for database errors."""
    message: str = "Database operation failed"
    error_code: str = "DATABASE_ERROR"
    error_type: str = "server_error"


class ExternalServiceErrorResponse(ErrorResponse):
    """Response for external service errors."""
    message: str = "External service error"
    error_code: str = "EXTERNAL_SERVICE_ERROR"
    error_type: str = "service_error"
    service_name: Optional[str] = Field(None, description="Name of the external service")


class TimeoutErrorResponse(ErrorResponse):
    """Response for timeout errors."""
    message: str = "Request timeout"
    error_code: str = "TIMEOUT_ERROR"
    error_type: str = "timeout_error"
    timeout_duration: Optional[float] = Field(None, description="Timeout duration in seconds")


class ConfigurationErrorResponse(ErrorResponse):
    """Response for configuration errors."""
    message: str = "Configuration error"
    error_code: str = "CONFIGURATION_ERROR"
    error_type: str = "server_error"
    config_key: Optional[str] = Field(None, description="Configuration key that caused the error")


# Common response type aliases
SuccessResponseDict = SuccessResponse[Dict[str, Any]]
SuccessResponseList = SuccessResponse[List[Dict[str, Any]]]
SuccessResponseStr = SuccessResponse[str]
SuccessResponseInt = SuccessResponse[int]
SuccessResponseBool = SuccessResponse[bool]
