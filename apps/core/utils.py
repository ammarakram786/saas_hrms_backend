"""
Core utilities for the HRMS application.
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import jwt
from django.conf import settings


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


def generate_invitation_token(email: str, tenant_id: str, role_ids: list) -> str:
    """
    Generate an invitation token for user invites.
    """
    payload = {
        'type': 'invitation',
        'email': email,
        'tenant_id': tenant_id,
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


class TenantContext:
    """
    Context manager for tenant-specific operations.
    """
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
