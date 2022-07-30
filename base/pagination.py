from collections import OrderedDict
from math import ceil

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class LargeResultsSetPagination(PageNumberPagination):
    # default_limit = api_settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 10000

    def get_page_size(self, request):
        self.page_size = super(LargeResultsSetPagination, self).get_page_size(request)
        return self.page_size

    def get_paginated_response(self, data):
        total_pages = ceil(self.page.paginator.count / self.page_size)
        current_page = self.page.number
        pagination = {'total_pages': total_pages, 'current_page': current_page,
                      'total_record': self.page.paginator.count, 'next': self.get_next_link(),
                      'previous': self.get_previous_link()}

        return Response(OrderedDict([
            ('pagination', pagination),
            ('results', data),
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                "pagination": {
                    'type': 'object',
                    'properties': {
                        "total_pages": {
                            'type': 'integer',
                            'example': 100,
                            'description': '总共（最大）页数'
                        },
                        "current_page": {
                            'type': 'integer',
                            'example': 2,
                            'description': '当前页数'
                        },
                        "total_record": {
                            'type': 'integer',
                            'example': 500,
                            'description': '总共记录数量'
                        },
                        'next': {
                            'type': 'string',
                            'nullable': True,
                            'format': 'uri',
                            'example': 'http://api.example.org/accounts/?page=3',
                            'description': '下一页'
                        },
                        'previous': {
                            'type': 'string',
                            'nullable': True,
                            'format': 'uri',
                            'example': 'http://api.example.org/accounts/?page=1',
                            'description': '上一页'
                        },
                    },
                },

                'results': schema,
            },
        }
