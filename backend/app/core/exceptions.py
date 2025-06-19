"""
Custom exception classes for the application.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    """Base custom HTTP exception with additional error code."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class DatabaseException(CustomHTTPException):
    """Database-related exceptions."""
    
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
        )


class ValidationException(CustomHTTPException):
    """Validation-related exceptions."""

    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


class ConfigurationException(CustomHTTPException):
    """Configuration-related exceptions."""

    def __init__(self, detail: str = "Configuration error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="CONFIGURATION_ERROR",
        )


class AuthenticationException(CustomHTTPException):
    """Authentication-related exceptions."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
        )


class AuthorizationException(CustomHTTPException):
    """Authorization-related exceptions."""
    
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR",
        )


class NotFoundException(CustomHTTPException):
    """Resource not found exceptions."""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
        )


class ConflictException(CustomHTTPException):
    """Resource conflict exceptions."""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT",
        )


class RateLimitException(CustomHTTPException):
    """Rate limiting exceptions."""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
        )


class ExternalServiceException(CustomHTTPException):
    """External service-related exceptions."""
    
    def __init__(self, detail: str = "External service error"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code="EXTERNAL_SERVICE_ERROR",
        )


class GeminiAPIException(ExternalServiceException):
    """Gemini API-specific exceptions."""
    
    def __init__(self, detail: str = "Gemini API error"):
        super().__init__(detail=detail)
        self.error_code = "GEMINI_API_ERROR"


class CrewAIException(CustomHTTPException):
    """CrewAI-specific exceptions."""
    
    def __init__(self, detail: str = "CrewAI operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="CREWAI_ERROR",
        )


class AgentException(CustomHTTPException):
    """Agent-specific exceptions."""
    
    def __init__(self, detail: str = "Agent operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="AGENT_ERROR",
        )


class ProjectException(CustomHTTPException):
    """Project-specific exceptions."""
    
    def __init__(self, detail: str = "Project operation failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="PROJECT_ERROR",
        )


class SessionException(CustomHTTPException):
    """Session-specific exceptions."""
    
    def __init__(self, detail: str = "Session operation failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="SESSION_ERROR",
        )
