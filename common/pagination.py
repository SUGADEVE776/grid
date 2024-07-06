from rest_framework.pagination import PageNumberPagination


class BasePagination(PageNumberPagination):
    """
    Pagination class used across the app.
    """

    page_size = 24
    page_size_query_param = "page-size"
    max_page_size = 100
