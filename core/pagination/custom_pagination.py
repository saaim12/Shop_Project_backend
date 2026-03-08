from rest_framework.pagination import PageNumberPagination, CursorPagination

class CustomPagination(PageNumberPagination):
    """
    Custom pagination class for list views.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_size_query_description = 'Number of results to return per page'
    max_page_size = 100

class CursorPaginationClass(CursorPagination):
    """
    Cursor pagination for better performance on large datasets.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-created_at'
