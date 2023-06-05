from rest_framework import pagination


class UsersPaginator(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
