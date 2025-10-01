"""
Core utilities for the HRMS application.
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import logging
import traceback

import jwt
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response


def generate_jwt_token(payload: Dict[str, Any], expires_in: Optional[int] = None) -> str:
    """
    Generate a JWT token with the given payload.
    
    Args:
        payload: Data to encode in the token
        expires_in: Token expiration time in seconds
    
    Returns:
        Encoded JWT token
    """
    if expires_in is None:
        expires_in = settings.JWT_ACCESS_TOKEN_LIFETIME
    
    payload.update({
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    })
    
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token and return its payload.
    
    Args:
        token: JWT token to decode
    
    Returns:
        Decoded payload
    
    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )


def generate_invitation_token(email: str, role_ids: list) -> str:
    """
    Generate an invitation token for user invites.
    """
    payload = {
        'type': 'invitation',
        'email': email,
        'role_ids': role_ids,
    }
    # Invitation tokens expire in 7 days
    return generate_jwt_token(payload, expires_in=7 * 24 * 60 * 60)


def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Get the user agent from the request.
    """
    return request.META.get('HTTP_USER_AGENT', '')


def validate_uuid(uuid_str: str) -> bool:
    """
    Validate if a string is a valid UUID.
    """
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False


# Enhanced Error Handling Utilities
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error class."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, error_code: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code or 'API_ERROR'


class ValidationError(APIError):
    """Validation error."""
    def __init__(self, message: str, field_errors: Dict[str, Any] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, 'VALIDATION_ERROR')
        self.field_errors = field_errors or {}


class NotFoundError(APIError):
    """Resource not found error."""
    def __init__(self, resource: str = 'Resource'):
        super().__init__(f'{resource} not found', status.HTTP_404_NOT_FOUND, 'NOT_FOUND')


class PermissionError(APIError):
    """Permission denied error."""
    def __init__(self, message: str = 'Permission denied'):
        super().__init__(message, status.HTTP_403_FORBIDDEN, 'PERMISSION_DENIED')


class AuthenticationError(APIError):
    """Authentication error."""
    def __init__(self, message: str = 'Authentication required'):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, 'AUTHENTICATION_ERROR')


def handle_exception(exc: Exception) -> Response:
    """
    Enhanced exception handler for API views.

    Args:
        exc: The exception that occurred

    Returns:
        Response with appropriate error details
    """
    from rest_framework.views import exception_handler

    logger.error(f"API Error: {str(exc)}", exc_info=True)

    # Handle our custom API errors
    if isinstance(exc, APIError):
        error_data = {
            'error': {
                'message': str(exc),
                'code': exc.error_code,
                'status_code': exc.status_code
            }
        }

        # Add field errors for validation errors
        if isinstance(exc, ValidationError) and exc.field_errors:
            error_data['error']['field_errors'] = exc.field_errors

        return Response(error_data, status=exc.status_code)

    # Handle Django validation errors
    elif isinstance(exc, DjangoValidationError):
        error_data = {
            'error': {
                'message': 'Validation failed',
                'code': 'VALIDATION_ERROR',
                'status_code': status.HTTP_400_BAD_REQUEST,
                'field_errors': exc.message_dict if hasattr(exc, 'message_dict') else {'general': str(exc)}
            }
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

    # Handle database integrity errors
    elif isinstance(exc, IntegrityError):
        error_data = {
            'error': {
                'message': 'Data integrity constraint violation',
                'code': 'INTEGRITY_ERROR',
                'status_code': status.HTTP_400_BAD_REQUEST
            }
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

    # Handle JWT errors
    elif hasattr(exc, '__class__') and 'jwt' in str(exc.__class__.__module__):
        error_data = {
            'error': {
                'message': 'Invalid or expired token',
                'code': 'TOKEN_ERROR',
                'status_code': status.HTTP_401_UNAUTHORIZED
            }
        }
        return Response(error_data, status=status.HTTP_401_UNAUTHORIZED)

    # Default server error
    error_data = {
        'error': {
            'message': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    }

    return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def api_view_error_handler(view_func):
    """
    Decorator to wrap view functions with enhanced error handling.

    Args:
        view_func: The view function to wrap

    Returns:
        Wrapped view function
    """
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except Exception as exc:
            return handle_exception(exc)
    return wrapper


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Tuple[bool, list]:
    """
    Validate that required fields are present in data.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, list_of_missing_fields)
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)

    return len(missing_fields) == 0, missing_fields


def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.

    Args:
        input_string: Input string to sanitize

    Returns:
        Sanitized string
    """
    import html
    return html.escape(input_string.strip())


def log_api_request(request, response, view_name: str = None):
    """
    Log API request details for monitoring.

    Args:
        request: The request object
        response: The response object
        view_name: Name of the view being called
    """
    try:
        logger.info(
            "API Request",
            extra={
                'method': request.method,
                'path': request.path,
                'user': getattr(request.user, 'email', 'Anonymous'),
                'ip': get_client_ip(request),
                'user_agent': get_user_agent(request)[:200],  # Truncate long user agents
                'status_code': response.status_code,
                'view': view_name,
                'response_time_ms': getattr(response, 'response_time', 'unknown')
            }
        )
    except Exception as log_exc:
        logger.error(f"Failed to log API request: {str(log_exc)}")


# Caching Utilities
from django.core.cache import cache
from django.conf import settings


def get_cache_key(request, view_name: str, prefix: str = 'api_response') -> str:
    """
    Generate a cache key for API responses.

    Args:
        request: The request object
        view_name: Name of the view
        prefix: Cache key prefix

    Returns:
        Cache key string
    """
    # Include user info for personalized caching
    user_id = getattr(request.user, 'id', 'anonymous')

    # Include query parameters for different responses
    query_params = sorted(request.GET.items()) if request.GET else []

    # Create unique key based on request details
    key_components = [
        prefix,
        view_name,
        str(user_id),
        str(query_params),
    ]

    # Create hash for consistent key length
    import hashlib
    key_string = '|'.join(key_components)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    return f"{prefix}:{view_name}:{key_hash}"


def cache_api_response(timeout: int = None):
    """
    Decorator to cache API responses.

    Args:
        timeout: Cache timeout in seconds (uses default if None)

    Returns:
        Decorated function
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Only cache GET requests
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)

            # Generate cache key
            view_name = view_func.__name__
            cache_key = get_cache_key(request, view_name)

            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                # Return cached response (reconstruct Django response)
                from django.http import JsonResponse
                return JsonResponse(cached_response['data'], status=cached_response['status'])

            # Execute view and cache response
            response = view_func(request, *args, **kwargs)

            # Only cache successful responses
            if (hasattr(response, 'status_code') and
                200 <= response.status_code < 300 and
                hasattr(response, 'data')):

                cache_data = {
                    'data': response.data,
                    'status': response.status_code
                }

                cache_timeout = timeout or settings.CACHE_TIMEOUTS.get('medium', 300)
                cache.set(cache_key, cache_data, cache_timeout)

            return response
        return wrapper
    return decorator


def clear_cache_pattern(pattern: str):
    """
    Clear cache entries matching a pattern.

    Args:
        pattern: Cache key pattern to clear
    """
    # Note: This is a simple implementation
    # In production, you might want to use more sophisticated cache invalidation
    cache.clear()


def invalidate_user_cache(user_id: int):
    """
    Invalidate all cache entries for a specific user.

    Args:
        user_id: User ID to invalidate cache for
    """
    # This is a basic implementation
    # You might want to track cache keys per user for more precise invalidation
    pattern = f"*:user_{user_id}:*"
    clear_cache_pattern(pattern)


