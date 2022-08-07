import os
import pathlib
import random
import string
import time
import traceback

import requests
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from base.dataclass import BaseOperatingRes
from base.utils import cache
from base.utils.cache import IBaseCache
from base.utils.format import format_completed_process
from base.utils.logger import plog
from base.viewset import BaseModelViewSet
from common.models import User
from common.serializers.operating import OperatingResSerializer
from website.applications.core.dataclass import BaseSSLCertificate
from website.models import Website
from website.serializers.website import WebsiteModelSerializer
from website.utils.certificate import issuing_certificate
from website.utils.domain import domain_is_resolved


class WebsiteView(BaseModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Website.objects.select_related('user').all()
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

    # @extend_schema(responses= todo add schema)
    @action(methods=['get'], detail=True)
    def get_ssl_info(self, request, *args, **kwargs):
        instance = self.get_object()
        certificate_path = instance.ssl_config['path']['certificate']
        if certificate_path != '' and pathlib.Path(certificate_path).exists():
            try:
                cert = BaseSSLCertificate.get_certificate(certificate_path)
                return Response(cert.__dict__)
            except Exception:
                e = traceback.format_exc()
                return Response(e, status=500)

        else:
            return Response('Not found', status=404)

    def update(self, request, *args, **kwargs):
        domain = request.data.get('domain', None)
        instance = self.get_object()
        if domain and domain != instance.domain:
            plog.debug("Due to the change of the primary domain name, delete the original configuration.")
            os.system(f"rm -rf  /etc/nginx/sites-enabled/{instance.domain}.conf")
        return super(WebsiteView, self).update(request, args, kwargs)

    def partial_update(self, request, *args, **kwargs):

        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['post'], detail=True, serializer_class=OperatingResSerializer)
    def enable_ssl(self, request):
        obj: Website = self.get_object()
        op = domain_is_resolved(obj.domain, request)
        if op.is_success():
            p = issuing_certificate(obj)
            if p.returncode != 0:
                op.msg = 'issue certificate error:\n' + format_completed_process(p)
                op.set_failure()
            else:
                obj.ssl_enable = True
                obj.save(update_fields=['ssl_enable'])

        return Response(op.json())

    @action(methods=['post'], detail=True, serializer_class=OperatingResSerializer)
    def disable_ssl(self, request):
        op = BaseOperatingRes()
        obj = self.get_object()
        obj.ssl_enable = False
        obj.save(update_fields=['ssl_enable'])
        op.set_success()
        return Response(op.json())

    @extend_schema(parameters=[OpenApiParameter(name='domain', type=str)])
    @action(methods=["get"], detail=False, serializer_class=OperatingResSerializer)
    def verify_dns_records(self, request: Request, *args, **kwargs):
        domain = request.query_params("domain")
        op = domain_is_resolved(domain, request)
        return Response(op.json())

    @extend_schema(parameters=[OpenApiParameter(name='domain', type=str)])
    @action(methods=["get"], detail=False, serializer_class=OperatingResSerializer)
    def domain_records(self, request: Request, *args, **kwargs):
        _cache = IBaseCache()
        op = BaseOperatingRes()
        op.set_processing()
        domain = request.query_params.get("domain")
        random_str = _cache.get(domain, "null")
        op.msg = random_str
        op.set_success()
        return Response(op.json())

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
