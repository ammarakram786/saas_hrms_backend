"""
Core middleware for logging and monitoring.
"""
import time
import json
import logging
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger(__name__)


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests and responses with performance metrics.
    """

    def process_request(self, request):
        """Log the start of API request."""
        if request.path.startswith('/api/'):
            request.start_time = time.time()

            # Log request details
            logger.info(
                "API Request Started",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'user': getattr(request.user, 'email', 'Anonymous') if request.user else 'Anonymous',
                    'ip': self.get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
                    'content_type': request.META.get('CONTENT_TYPE', ''),
                    'query_params': dict(request.GET) if request.GET else {},
                }
            )

    def process_response(self, request, response):
        """Log the completion of API request."""
        if request.path.startswith('/api/') and hasattr(request, 'start_time'):
            duration = time.time() - request.start_time

            # Log response details
            logger.info(
                "API Request Completed",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'user': getattr(request.user, 'email', 'Anonymous') if request.user else 'Anonymous',
                    'ip': self.get_client_ip(request),
                    'response_size': len(response.content) if hasattr(response, 'content') else 0,
                }
            )

        return response

    def process_exception(self, request, exception):
        """Log exceptions in API requests."""
        if request.path.startswith('/api/'):
            logger.error(
                "API Request Exception",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'user': getattr(request.user, 'email', 'Anonymous') if request.user else 'Anonymous',
                    'ip': self.get_client_ip(request),
                    'exception_type': type(exception).__name__,
                    'exception_message': str(exception),
                },
                exc_info=True
            )

    def get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor performance metrics.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Track view execution time."""
        if request.path.startswith('/api/'):
            request.view_start_time = time.time()

    def process_response(self, request, response):
        """Log performance metrics."""
        if request.path.startswith('/api/') and hasattr(request, 'view_start_time'):
            view_duration = time.time() - request.view_start_time

            # Log slow requests
            if view_duration > 1.0:  # More than 1 second
                logger.warning(
                    "Slow API Request",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'duration_ms': round(view_duration * 1000, 2),
                        'status_code': response.status_code,
                        'user': getattr(request.user, 'email', 'Anonymous') if request.user else 'Anonymous',
                    }
                )

        return response
