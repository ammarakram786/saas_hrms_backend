"""
Custom throttling classes for API rate limiting.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class LoginRateThrottle(UserRateThrottle):
    """
    Throttle class for login attempts.
    More restrictive for login to prevent brute force attacks.
    """
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """
    Throttle class for registration attempts.
    More restrictive for registration to prevent spam.
    """
    scope = 'register'


class SensitiveOperationThrottle(UserRateThrottle):
    """
    Throttle class for sensitive operations like password changes, deletions, etc.
    """
    scope = 'sensitive'


class GeneralUserThrottle(UserRateThrottle):
    """
    General throttling for authenticated users.
    """
    scope = 'user'


class GeneralAnonThrottle(AnonRateThrottle):
    """
    General throttling for anonymous users.
    """
    scope = 'anon'
