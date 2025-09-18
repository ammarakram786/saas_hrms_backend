"""
JWT Authentication for the HRMS application.
"""
import jwt
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
from rest_framework.authentication import BaseAuthentication

from apps.core.utils import decode_jwt_token

logger = logging.getLogger(__name__)
User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication class.
    """
    authentication_header_prefix = 'Bearer'
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()
        
        if not auth_header:
            return None
        
        if len(auth_header) == 1:
            # Invalid token header. No credentials provided.
            return None
        
        elif len(auth_header) > 2:
            # Invalid token header. Token string should not contain spaces.
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
        
        # The JWT library we're using can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # we simply have to decode `prefix` and `token`. This does not make for
        # clean code, but it is a good decision because we would get an error
        # if we didn't decode these values.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')
        
        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expected. Do not attempt to
            # authenticate.
            return None
        
        # Now, try to authenticate the given credentials.
        return self._authenticate_credentials(request, token)
    
    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            payload = decode_jwt_token(token)
        except jwt.ExpiredSignatureError:
            msg = 'Token has expired.'
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            msg = 'Invalid token.'
            raise exceptions.AuthenticationFailed(msg)
        
        user = self._get_user_from_payload(payload)
        
        if user is None:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)
        
        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)
        
        return (user, payload)
    
    def _get_user_from_payload(self, payload):
        """
        Get user from JWT payload.
        """
        try:
            user_id = payload.get('user_id')
            if not user_id:
                return None
            
            user = User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            logger.warning(f"User with ID {payload.get('user_id')} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting user from payload: {e}")
            return None


def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for a user.
    """
    from apps.core.utils import generate_jwt_token
    
    # Base payload
    payload = {
        'user_id': str(user.id),
        'email': user.email,
        'tenant_id': str(user.tenant_id) if user.tenant_id else None,
        'is_superuser': user.is_superuser,
    }
    
    # Add tenant-specific data for non-superusers
    if not user.is_superuser and user.tenant_id:
        payload.update({
            'role_ids': [str(role.id) for role in user.get_tenant_roles()],
            'permissions': user.effective_permissions,
        })
    
    # Generate tokens
    access_token = generate_jwt_token(
        payload,
        expires_in=settings.JWT_ACCESS_TOKEN_LIFETIME
    )
    
    refresh_payload = {
        'user_id': str(user.id),
        'type': 'refresh',
    }
    refresh_token = generate_jwt_token(
        refresh_payload,
        expires_in=settings.JWT_REFRESH_TOKEN_LIFETIME
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': settings.JWT_ACCESS_TOKEN_LIFETIME,
    }


def refresh_access_token(refresh_token):
    """
    Generate a new access token from a refresh token.
    """
    try:
        payload = decode_jwt_token(refresh_token)
        
        if payload.get('type') != 'refresh':
            raise exceptions.AuthenticationFailed('Invalid token type')
        
        user_id = payload.get('user_id')
        user = User.objects.get(id=user_id)
        
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User is inactive')
        
        # Generate new access token
        tokens = generate_tokens_for_user(user)
        
        return {
            'access_token': tokens['access_token'],
            'token_type': 'Bearer',
            'expires_in': settings.JWT_ACCESS_TOKEN_LIFETIME,
        }
        
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed('Refresh token has expired')
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed('Invalid refresh token')
    except User.DoesNotExist:
        raise exceptions.AuthenticationFailed('User not found')
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise exceptions.AuthenticationFailed('Token refresh failed')
