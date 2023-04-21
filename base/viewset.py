from django_filters import rest_framework
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet


class ExtraViewMethodSetMixin(ReadOnlyModelViewSet):
    def get_client_ip(self, request):
        if request is None:
            import requests

            res = requests.get("https://www.taobao.com/help/getip.php")
            ip = res.text.split('"')[1]
            return ip

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_list = x_forwarded_for.split(",")
            ip = ip_list
        else:
            ip = request.META.get("REMOTE_ADDR", None)
        if ip is None or ip == "127.0.0.1":
            import requests

            res = requests.get("https://www.taobao.com/help/getip.php")
            ip = res.text.split('"')[1]

        return ip

    @staticmethod
    def base_response(
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        return Response(
            data,
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )


class BaseReadOnlyModelViewSet(ExtraViewMethodSetMixin, ReadOnlyModelViewSet):
    filter_backends = (
        rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )


class BaseModelViewSet(ExtraViewMethodSetMixin, viewsets.ModelViewSet):
    filter_backends = (
        rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
