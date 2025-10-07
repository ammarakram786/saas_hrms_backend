"""
Authentication views.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout

from ..serializers import LoginSerializer, RegisterSerializer, UserSerializer
from ..authentication import generate_tokens_for_user, refresh_access_token
from ...core.utils import (
    api_view_error_handler, APIError, ValidationError,
    validate_required_fields, log_api_request
)
from ...core.throttling import LoginRateThrottle, RegisterRateThrottle


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
@api_view_error_handler
def login_view(request):
    """
    User login endpoint with enhanced validation, error handling, and rate limiting.
    """
    try:
        # Validate required fields
        is_valid, missing_fields = validate_required_fields(
            request.data, ['email', 'password']
        )
        if not is_valid:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                field_errors={field: f'{field} is required' for field in missing_fields}
            )

        serializer = LoginSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            raise ValidationError(
                'Login validation failed',
                field_errors=serializer.errors
            )

        user = serializer.validated_data['user']

        # Check if user is active
        if not user.is_active:
            raise APIError(
                'Account is deactivated. Please contact your administrator.',
                status.HTTP_403_FORBIDDEN,
                'ACCOUNT_DEACTIVATED'
            )

        # Check for failed login attempts (simple rate limiting)
        from django.core.cache import cache
        failed_attempts_key = f"failed_login_attempts:{user.email}"
        failed_attempts = cache.get(failed_attempts_key, 0)

        if failed_attempts >= 5:
            # Account is temporarily locked due to too many failed attempts
            raise APIError(
                'Account temporarily locked due to too many failed login attempts. Please try again later.',
                status.HTTP_423_LOCKED,
                'ACCOUNT_LOCKED'
            )

        # Generate tokens
        tokens = generate_tokens_for_user(user)

        # Update last login
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        # Serialize user data for response
        user_serializer = UserSerializer(user)
        
        response_data = {
            'user': user_serializer.data,
            **tokens
        }

        # Clear failed login attempts on successful login
        cache.delete(failed_attempts_key)

        # Log successful login
        log_api_request(request, type('Response', (), {'status_code': status.HTTP_200_OK})(), 'login_view')

        return Response(response_data)

    except ValidationError:
        # Track failed login attempts
        if 'user' in locals():
            failed_attempts_key = f"failed_login_attempts:{user.email}"
            cache.set(failed_attempts_key, cache.get(failed_attempts_key, 0) + 1, 300)  # 5 minutes
        raise
    except APIError:
        raise
    except Exception as exc:
        # Log unexpected errors
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in login_view: {str(exc)}", exc_info=True)
        raise APIError('Login failed due to an internal error', status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint.
    """
    logout(request)
    return Response({'message': 'Logged out successfully'})


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh access token endpoint.
    """
    refresh_token = request.data.get('refresh_token')

    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tokens = refresh_access_token(refresh_token)
        return Response(tokens)
    except Exception as e:
        return Response(
            {'error': 'Invalid refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterRateThrottle])
@api_view_error_handler
def register_view(request):
    """
    User registration endpoint with enhanced validation and error handling.
    """
    try:
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        is_valid, missing_fields = validate_required_fields(request.data, required_fields)
        if not is_valid:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                field_errors={field: f'{field} is required' for field in missing_fields}
            )

        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, request.data['email']):
            raise ValidationError(
                'Invalid email format',
                field_errors={'email': 'Please provide a valid email address'}
            )

        # Validate password strength
        password = request.data.get('password', '')
        if len(password) < 8:
            raise ValidationError(
                'Password too weak',
                field_errors={'password': 'Password must be at least 8 characters long'}
            )

        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            raise ValidationError(
                'Registration validation failed',
                field_errors=serializer.errors
            )

        user = serializer.save()

        # Generate tokens
        tokens = generate_tokens_for_user(user)

        response_data = {
            'user': serializer.data,
            **tokens,
            'message': 'User registered successfully'
        }

        # Log successful registration
        log_api_request(request, type('Response', (), {'status_code': status.HTTP_201_CREATED})(), 'register_view')

        return Response(response_data, status=status.HTTP_201_CREATED)

    except ValidationError:
        raise
    except Exception as exc:
        # Log unexpected errors
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in register_view: {str(exc)}", exc_info=True)
        raise APIError('Registration failed due to an internal error', status.HTTP_500_INTERNAL_SERVER_ERROR)


