import pathlib
import traceback

from django.db import transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from base.dataclass import BaseOperatingRes
from base.utils.cache import IBaseCache
from base.utils.format import format_completed_process
from base.viewset import BaseModelViewSet
from common.models import User
from common.serializers.operating import OperatingResSerializer
from website.applications.core.dataclass import BaseSSLCertificate
from website.models import Website
from website.serializers.website import (
    DefaultWebsuteConfigSerializer,
    WebsiteConfigSerializer,
    WebsiteDomainConfigSerializer,
    WebsiteModelSerializer,
)
from website.utils.certificate import issuing_certificate
from website.utils.domain import domain_is_resolved, find_domain_in_nginx


class WebsiteView(BaseModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Website.objects.select_related("user").all()
    serializer_class = WebsiteModelSerializer

    def get_queryset(self):
        user: User = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        else:
            return self.queryset.filter(user=user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(WebsiteView, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # @extend_schema(responses= todo add schema)
    @action(methods=["get"], detail=True)
    def get_ssl_info(self, request, *args, **kwargs):
        instance = self.get_object()
        certificate_path = instance.ssl_config["path"]["certificate"]
        if certificate_path != "" and pathlib.Path(certificate_path).exists():
            try:
                cert = BaseSSLCertificate.get_certificate(certificate_path)
                return Response(cert.__dict__)
            except Exception:
                e = traceback.format_exc()
                return Response(e, status=500)

        else:
            return Response("Not found", status=404)

    @action(
        methods=["post"], detail=True, serializer_class=WebsiteDomainConfigSerializer
    )
    def update_domain(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        serializer = WebsiteDomainConfigSerializer(data=request.data, instance=obj)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return Response(data)

    @action(methods=["post"], detail=True, serializer_class=WebsiteConfigSerializer)
    def update_web_config(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = WebsiteConfigSerializer(data=request.data, instance=obj)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return Response({"web_server_config": data})

    @action(methods=["post"], detail=True, serializer_class=OperatingResSerializer)
    def enable_ssl(self, request, *args, **kwargs):
        obj: Website = self.get_object()
        op = BaseOperatingRes()

        p = issuing_certificate(obj)
        if p.returncode != 0:
            op.msg = "issue certificate error:\n" + format_completed_process(p)
            op.set_failure()
            obj.get_application().toggle_ssl(False)
        else:
            obj.ssl_enable = True
            obj.sync_web_config(save=True)
            obj.get_application().toggle_ssl(True)

        return Response(op.json())

    @action(methods=["post"], detail=True, serializer_class=OperatingResSerializer)
    def disable_ssl(self, request, *args, **kwargs):
        op = BaseOperatingRes()
        obj: Website = self.get_object()
        obj.ssl_enable = False
        obj.sync_web_config(save=True)
        op.set_success()
        return Response(op.json())

    @extend_schema(parameters=[OpenApiParameter(name="domain", type=str)])
    @action(methods=["get"], detail=False, serializer_class=OperatingResSerializer)
    def verify_dns_records(self, request: Request, *args, **kwargs):
        """
        如果 UISSH 没有启用SSL直接返回失败，否则进行域名解析判断流程。

        If SSL is not enabled for UISSH, it returns a failure directly;
        otherwise, the domain name resolution and verification process are carried out.
        """
        if not find_domain_in_nginx():
            op = BaseOperatingRes()
            # op.set_failure("UISSH 没有启用SSL，无法进行域名解析判断。")
            op.set_failure(
                "Without enabling SSL "
                "UISSH cannot perform domain name resolution and verification."
            )
            return Response(op.json())

        domain = request.query_params.get("domain")
        op = domain_is_resolved(domain, request)
        return Response(op.json())

    @extend_schema(parameters=[OpenApiParameter(name="domain", type=str)])
    @action(methods=["get"], detail=False, serializer_class=OperatingResSerializer)
    def domain_records(self, request: Request, *args, **kwargs):
        """
        用于域名解析判断流程中的第二步，获取随机字符串用来核对。
        It is used in the second step of the domain name resolution judgment process to obtain random strings for checking.
        """
        _cache = IBaseCache()
        op = BaseOperatingRes()
        op.set_processing()
        domain = request.query_params.get("domain")
        random_str = _cache.get(domain, "null")
        op.msg = random_str
        op.set_success()
        return Response(op.json())

    @action(
        methods=["get"], detail=True, serializer_class=DefaultWebsuteConfigSerializer
    )
    def get_default_nginx_config(self, request, *args, **kwargs):
        """
        获取提供给用户的默认 nginx 配置文件。
        Get the default nginx configuration file provided to the user.
        """
        obj: Website = self.get_object()
        serializer = DefaultWebsuteConfigSerializer(
            instance=obj, data={"web_server_config": obj.valid_web_server_config}
        )

        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return Response(data)
