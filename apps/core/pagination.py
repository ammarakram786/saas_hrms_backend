"""
Custom pagination classes.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination with per_page query parameter support.
    """
    page_size = 20
    page_size_query_param = 'per_page'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return a paginated style Response object.
        """
        return Response({
            'success': True,
            'data': data,
            'pagination': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'page_size': self.page.paginator.per_page,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            }
        })


class LargeResultsSetPagination(CustomPageNumberPagination):
    """
    Pagination for large result sets.
    """
    page_size = 50
    max_page_size = 200


class SmallResultsSetPagination(CustomPageNumberPagination):
    """
    Pagination for small result sets.
    """
    page_size = 10
    max_page_size = 50
