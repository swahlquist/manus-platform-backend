"""
Error handling utilities for the Manus Backend.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

logger = logging.getLogger("manus-backend.utils.errors")

class ManusBadRequestError(HTTPException):
    """Exception for bad request errors."""
    
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ManusUnauthorizedError(HTTPException):
    """Exception for unauthorized errors."""
    
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ManusNotFoundError(HTTPException):
    """Exception for not found errors."""
    
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ManusProviderError(HTTPException):
    """Exception for provider errors."""
    
    def __init__(self, detail: str, provider: Optional[str] = None):
        error_detail = {"message": detail}
        if provider:
            error_detail["provider"] = provider
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=error_detail)

class ManusInternalError(HTTPException):
    """Exception for internal server errors."""
    
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

def format_error_response(status_code: int, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format error response.
    
    Args:
        status_code: HTTP status code.
        message: Error message.
        details: Additional error details.
        
    Returns:
        Formatted error response.
    """
    response = {
        "error": {
            "status_code": status_code,
            "message": message
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response
